import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db import get_connection
from datetime import datetime, timedelta


def _insert_log(cur, staff_id, action, target_id, detail=""):
    cur.execute("""
        INSERT INTO AuditLog (StaffID, Action, TargetID, Timestamp, Detail)
        VALUES (?, ?, ?, ?, ?)
    """, (
        staff_id,
        action,
        str(target_id),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        detail,
    ))



def write_log(staff_id, action, target_id, detail=""):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        _insert_log(cur, staff_id, action, target_id, detail)
        conn.commit()
    except Exception as e:
        print(f"[Log] {e}")
    finally:
        if conn:
            conn.close()


def get_fine_per_day():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT FeePerDay FROM FineRule ORDER BY EffectiveDate DESC LIMIT 1")
    row = cur.fetchone(); conn.close()
    return row[0] if row else 2000


def _validate_borrow(cur, student_id, book_id, current_active_count=None):
    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("SELECT Name, CardExpire, CardStatus FROM Students WHERE StudentID=?",
                (student_id,))
    sv = cur.fetchone()
    if not sv:
        return False, "Không tìm thấy độc giả."
    if sv["CardStatus"] == "blocked":
        return False, "Thẻ độc giả đã bị khóa do vi phạm. Vui lòng liên hệ thủ thư."
    if sv["CardExpire"] and sv["CardExpire"] < today:
        return False, "Thẻ thư viện đã hết hạn."

    cur.execute("SELECT Title, Available FROM Books WHERE BookID=?", (book_id,))
    bk = cur.fetchone()
    if not bk:
        return False, "Không tìm thấy sách."
    if bk["Available"] <= 0:
        return False, "Sách hiện không còn."

    if current_active_count is None:
        cur.execute("""
            SELECT COUNT(*) FROM Borrow
            WHERE StudentID=? AND Status IN ('Borrowing','Overdue')
        """, (student_id,))
        current_active_count = cur.fetchone()[0]
    if current_active_count >= 5:
        return False, "Độc giả đang mượn tối đa 5 cuốn."

    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status='Overdue'
    """, (student_id,))
    if cur.fetchone()[0] > 0:
        return False, "Độc giả có sách quá hạn chưa trả. Vui lòng xử lý trước."

    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status='Lost'
    """, (student_id,))
    if cur.fetchone()[0] > 0:
        return False, "Độc giả có sách bị mất chưa xử lý. Vui lòng liên hệ thủ thư."

    due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    return True, {"due": due, "book_title": bk["Title"]}



def borrow_book(student_id, book_id):
    conn = get_connection(); cur = conn.cursor()

    ok, result = _validate_borrow(cur, student_id, book_id)
    if not ok:
        conn.close()
        return False, result

    due = result["due"]
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        INSERT INTO Borrow (StudentID,BookID,BorrowDate,DueDate,Status)
        VALUES (?,?,?,?,'Borrowing')
    """, (student_id, book_id, today, due))
    cur.execute(
        "UPDATE Books SET Available=Available-1 WHERE BookID=?", (book_id,))
    _insert_log(cur, "system", "Mượn sách", student_id,
              f"Sách: {book_id} | Hạn trả: {due}")
    conn.commit()
    conn.close()
    return True, f"Mượn thành công! Hạn trả: {due}"



def borrow_books(student_id, book_ids):
    normalized = []
    seen = set()
    for raw in book_ids:
        bid = (raw or "").strip()
        if not bid or bid in seen:
            continue
        normalized.append(bid)
        seen.add(bid)

    if not normalized:
        return False, "Vui lòng nhập ít nhất 1 mã sách.", []

    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status IN ('Borrowing','Overdue')
    """, (student_id,))
    active_count = cur.fetchone()[0]
    remaining = 5 - active_count
    if remaining <= 0:
        conn.close()
        return False, "Độc giả đang mượn tối đa 5 cuốn.", []

    success_ids = []
    failed = []
    today = datetime.now().strftime("%Y-%m-%d")

    for bid in normalized:
        if len(success_ids) >= remaining:
            failed.append((bid, "Vượt quá giới hạn tối đa 5 cuốn đang mượn."))
            continue
        ok, result = _validate_borrow(cur, student_id, bid, active_count + len(success_ids))
        if not ok:
            failed.append((bid, result))
            continue

        due = result["due"]
        cur.execute("""
            INSERT INTO Borrow (StudentID,BookID,BorrowDate,DueDate,Status)
            VALUES (?,?,?,?,'Borrowing')
        """, (student_id, bid, today, due))
        cur.execute("UPDATE Books SET Available=Available-1 WHERE BookID=?", (bid,))
        success_ids.append(bid)
        _insert_log(cur, "system", "Mượn sách", student_id,
                  f"Sách: {bid} | Hạn trả: {due}")

    conn.commit()
    conn.close()

    if not success_ids:
        first_error = failed[0][1] if failed else "Không thể mượn sách."
        return False, first_error, failed

    summary = f"Mượn thành công {len(success_ids)} cuốn"
    if failed:
        summary += f", thất bại {len(failed)} cuốn"
    summary += "."
    return True, summary, failed


def return_book(borrow_id):
    conn = get_connection(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT b.*, bk.Title FROM Borrow b
        JOIN Books bk ON b.BookID=bk.BookID
        WHERE b.BorrowID=?
    """, (borrow_id,))
    borrow = cur.fetchone()
    if not borrow:
        conn.close(); return False, "Không tìm thấy phiếu mượn.", 0

    fine = 0
    if borrow["DueDate"] < today:
        days = (datetime.strptime(today, "%Y-%m-%d") -
                datetime.strptime(borrow["DueDate"], "%Y-%m-%d")).days
        fine = days * get_fine_per_day()

    cur.execute("""
        UPDATE Borrow SET ReturnDate=?, Status='Returned', FineAmount=?
        WHERE BorrowID=?
    """, (today, fine, borrow_id))
    cur.execute(
        "UPDATE Books SET Available=Available+1 WHERE BookID=?",
        (borrow["BookID"],))
    _insert_log(cur, "system", "Trả sách", borrow["StudentID"],
              f"Sách: {borrow['BookID']} | Phạt: {fine:,.0f}đ")

    # Bo khoa the neu khong con qua han / mat sach
    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status IN ('Overdue','Lost')
        AND BorrowID != ?
    """, (borrow["StudentID"], borrow_id))
    if cur.fetchone()[0] == 0:
        cur.execute(
            "UPDATE Students SET CardStatus='active' WHERE StudentID=?",
            (borrow["StudentID"],))

    conn.commit(); conn.close()
    msg = f"Trả sách thành công!"
    if fine > 0:
        msg += f" Tiền phạt: {fine:,.0f}đ"
    return True, msg, fine


def mark_lost(borrow_id, fine_amount, staff_id=""):
    """Danh dau sach bi mat, tinh phat va khoa the sinh vien."""
    conn = get_connection(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("SELECT * FROM Borrow WHERE BorrowID=?", (borrow_id,))
    borrow = cur.fetchone()
    if not borrow:
        conn.close(); return False, "Không tìm thấy phiếu mượn."

    cur.execute("""
        UPDATE Borrow
        SET Status='Lost', LostDate=?, FineAmount=?
        WHERE BorrowID=?
    """, (today, fine_amount, borrow_id))

    # Khoa the sinh vien
    cur.execute(
        "UPDATE Students SET CardStatus='blocked' WHERE StudentID=?",
        (borrow["StudentID"],))

    # Ghi log
    if staff_id:
        _insert_log(cur, staff_id, "Mất sách", str(borrow_id),
              f"SV: {borrow['StudentID']} | Sách: {borrow['BookID']} | Phạt: {fine_amount:,.0f}đ")
    else:
        _insert_log(cur, "system", "Mất sách", str(borrow_id),
                  f"SV: {borrow['StudentID']} | Sách: {borrow['BookID']}")

    conn.commit(); conn.close()
    return True, f"Đã xử lý mất sách. Thẻ độc giả bị khóa. Tiền phạt: {fine_amount:,.0f}đ"


def resolve_lost(borrow_id, staff_id=""):
    """Giai quyet xong mat sach (da nop phat), mo khoa the."""
    conn = get_connection(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("SELECT * FROM Borrow WHERE BorrowID=?", (borrow_id,))
    borrow = cur.fetchone()
    if not borrow:
        conn.close(); return False, "Không tìm thấy phiếu mượn."

    cur.execute(
        "UPDATE Borrow SET FinePaid=1 WHERE BorrowID=?", (borrow_id,))

    # Kiem tra con vi pham nao khac khong
    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status IN ('Overdue','Lost')
        AND (FinePaid=0 OR FinePaid IS NULL)
        AND BorrowID != ?
    """, (borrow["StudentID"], borrow_id))
    if cur.fetchone()[0] == 0:
        cur.execute(
            "UPDATE Students SET CardStatus='active' WHERE StudentID=?",
            (borrow["StudentID"],))

    if staff_id:
        _insert_log(cur, staff_id, "Giải quyết mất sách", str(borrow_id),
              f"SV: {borrow['StudentID']} | Sách: {borrow['BookID']}")

    conn.commit(); conn.close()
    return True, "Đã giải quyết xong. Thẻ độc giả được mở khóa."


def get_active_borrows(keyword=""):
    conn = get_connection(); cur = conn.cursor()
    kw = f"%{keyword}%"
    cur.execute("""
        SELECT b.BorrowID, b.StudentID, s.Name as StudentName,
               bk.Title as BookTitle, b.BorrowDate, b.DueDate,
               b.Status, b.FineAmount, b.LostDate
        FROM Borrow b
        JOIN Students s  ON b.StudentID=s.StudentID
        JOIN Books bk    ON b.BookID=bk.BookID
        WHERE b.Status IN ('Borrowing','Overdue','Lost')
          AND (b.StudentID LIKE ? OR s.Name LIKE ? OR bk.Title LIKE ?)
        ORDER BY
            CASE b.Status
                WHEN 'Lost'     THEN 1
                WHEN 'Overdue'  THEN 2
                WHEN 'Borrowing' THEN 3
            END,
            b.DueDate ASC
    """, (kw, kw, kw))
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def update_overdue_status():
    conn = get_connection(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        UPDATE Borrow SET Status='Overdue'
        WHERE Status='Borrowing' AND DueDate < ?
    """, (today,))

    # Tinh lai tien phat cho sach qua han
    cur.execute("""
        SELECT BorrowID, DueDate FROM Borrow WHERE Status='Overdue'
    """)
    for row in cur.fetchall():
        days = (datetime.strptime(today,"%Y-%m-%d") -
                datetime.strptime(row["DueDate"],"%Y-%m-%d")).days
        fine = days * get_fine_per_day()
        cur.execute(
            "UPDATE Borrow SET FineAmount=? WHERE BorrowID=?",
            (fine, row["BorrowID"]))

    # Khoa the sinh vien qua han > 30 ngay
    cur.execute("""
        SELECT DISTINCT StudentID FROM Borrow
        WHERE Status='Overdue'
          AND CAST(julianday(?) - julianday(DueDate) AS INTEGER) > 30
    """, (today,))
    for (sid,) in cur.fetchall():
        cur.execute(
            "UPDATE Students SET CardStatus='blocked' WHERE StudentID=?", (sid,))

    conn.commit(); conn.close()


def get_dashboard_stats():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Books")
    total_books = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Students")
    total_students = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Borrow WHERE Status='Borrowing'")
    borrowing = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Borrow WHERE Status='Overdue'")
    overdue = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Borrow WHERE Status='Lost'")
    lost = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM Students WHERE CardStatus='blocked'
    """)
    blocked = cur.fetchone()[0]
    conn.close()
    return {
        "total_books":    total_books,
        "total_students": total_students,
        "borrowing":      borrowing,
        "overdue":        overdue,
        "lost":           lost,
        "blocked":        blocked,
    }