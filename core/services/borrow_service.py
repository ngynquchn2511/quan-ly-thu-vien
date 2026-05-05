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


def _send_email_bg(func, *args):
    """Gui email background, khong block UI."""
    import threading
    threading.Thread(target=func, args=args, daemon=True).start()


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
        return False, "Khong tim thay doc gia."
    if sv["CardStatus"] == "blocked":
        return False, "The doc gia da bi khoa do vi pham. Vui long lien he thu thu."
    if sv["CardExpire"] and sv["CardExpire"] < today:
        return False, "The thu vien da het han."

    cur.execute("SELECT Title, Available FROM Books WHERE BookID=?", (book_id,))
    bk = cur.fetchone()
    if not bk:
        return False, "Khong tim thay sach."
    if bk["Available"] <= 0:
        return False, "Sach hien khong con."

    if current_active_count is None:
        cur.execute("""
            SELECT COUNT(*) FROM Borrow
            WHERE StudentID=? AND Status IN ('Borrowing','Overdue')
        """, (student_id,))
        current_active_count = cur.fetchone()[0]
    if current_active_count >= 5:
        return False, "Doc gia dang muon toi da 5 cuon."

    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status='Overdue'
    """, (student_id,))
    if cur.fetchone()[0] > 0:
        return False, "Doc gia co sach qua han chua tra. Vui long xu ly truoc."

    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status='Lost'
    """, (student_id,))
    if cur.fetchone()[0] > 0:
        return False, "Doc gia co sach bi mat chua xu ly. Vui long lien he thu thu."

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
    cur.execute("UPDATE Books SET Available=Available-1 WHERE BookID=?", (book_id,))
    _insert_log(cur, "system", "Muon sach", student_id,
              f"Sach: {book_id} | Han tra: {due}")
    conn.commit()
    conn.close()
    return True, f"Muon thanh cong! Han tra: {due}"


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
        return False, "Vui long nhap it nhat 1 ma sach.", []

    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status IN ('Borrowing','Overdue')
    """, (student_id,))
    active_count = cur.fetchone()[0]
    remaining = 5 - active_count
    if remaining <= 0:
        conn.close()
        return False, "Doc gia dang muon toi da 5 cuon.", []

    success_ids = []
    failed = []
    today = datetime.now().strftime("%Y-%m-%d")

    for bid in normalized:
        if len(success_ids) >= remaining:
            failed.append((bid, "Vuot qua gioi han toi da 5 cuon dang muon."))
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
        _insert_log(cur, "system", "Muon sach", student_id,
                  f"Sach: {bid} | Han tra: {due}")

    conn.commit()
    conn.close()

    if not success_ids:
        first_error = failed[0][1] if failed else "Khong the muon sach."
        return False, first_error, failed

    summary = f"Muon thanh cong {len(success_ids)} cuon"
    if failed:
        summary += f", that bai {len(failed)} cuon"
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
        conn.close(); return False, "Khong tim thay phieu muon.", 0
    fine = 0
    if borrow["DueDate"] < today:
        days = (datetime.strptime(today, "%Y-%m-%d") -
                datetime.strptime(borrow["DueDate"], "%Y-%m-%d")).days
        fine = days * get_fine_per_day()
    cur.execute("""
        UPDATE Borrow SET ReturnDate=?, Status='Returned', FineAmount=?
        WHERE BorrowID=?
    """, (today, fine, borrow_id))
    cur.execute("UPDATE Books SET Available=Available+1 WHERE BookID=?", (borrow["BookID"],))
    _insert_log(cur, "system", "Tra sach", borrow["StudentID"],
              f"Sach: {borrow['BookID']} | Phat: {fine:,.0f}d")
    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status IN ('Overdue','Lost')
        AND BorrowID != ?
    """, (borrow["StudentID"], borrow_id))
    if cur.fetchone()[0] == 0:
        cur.execute("UPDATE Students SET CardStatus='active' WHERE StudentID=?",
                    (borrow["StudentID"],))
    conn.commit(); conn.close()
    msg = f"Tra sach thanh cong!"
    if fine > 0:
        msg += f" Tien phat: {fine:,.0f}d"
    return True, msg, fine


def mark_lost(borrow_id, fine_amount, staff_id=""):
    conn = get_connection(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT * FROM Borrow WHERE BorrowID=?", (borrow_id,))
    borrow = cur.fetchone()
    if not borrow:
        conn.close(); return False, "Khong tim thay phieu muon."

    cur.execute("""
        UPDATE Borrow SET Status='Lost', LostDate=?, FineAmount=?
        WHERE BorrowID=?
    """, (today, fine_amount, borrow_id))
    cur.execute("UPDATE Students SET CardStatus='blocked' WHERE StudentID=?",
                (borrow["StudentID"],))

    if staff_id:
        _insert_log(cur, staff_id, "Mat sach", str(borrow_id),
              f"SV: {borrow['StudentID']} | Sach: {borrow['BookID']} | Phat: {fine_amount:,.0f}d")
    else:
        _insert_log(cur, "system", "Mat sach", str(borrow_id),
                  f"SV: {borrow['StudentID']} | Sach: {borrow['BookID']}")

    # Lay thong tin email de gui
    cur.execute("SELECT Name, Email FROM Students WHERE StudentID=?", (borrow["StudentID"],))
    sv = cur.fetchone()
    conn.commit(); conn.close()

    # Gui email thong bao khoa the
    if sv and sv["Email"]:
        try:
            from core.services.email_service import notify_card_blocked
            _send_email_bg(notify_card_blocked,
                sv["Email"], sv["Name"],
                f"Sach bi mat - phieu #{borrow_id}", fine_amount)
        except Exception as e:
            print(f"[Email] {e}")

    return True, f"Da xu ly mat sach. The doc gia bi khoa. Tien phat: {fine_amount:,.0f}d"


def resolve_lost(borrow_id, staff_id=""):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT * FROM Borrow WHERE BorrowID=?", (borrow_id,))
    borrow = cur.fetchone()
    if not borrow:
        conn.close(); return False, "Khong tim thay phieu muon."

    cur.execute("UPDATE Borrow SET FinePaid=1 WHERE BorrowID=?", (borrow_id,))
    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND Status IN ('Overdue','Lost')
        AND (FinePaid=0 OR FinePaid IS NULL)
        AND BorrowID != ?
    """, (borrow["StudentID"], borrow_id))
    if cur.fetchone()[0] == 0:
        cur.execute("UPDATE Students SET CardStatus='active' WHERE StudentID=?",
                    (borrow["StudentID"],))
    if staff_id:
        _insert_log(cur, staff_id, "Giai quyet mat sach", str(borrow_id),
              f"SV: {borrow['StudentID']} | Sach: {borrow['BookID']}")

    # Lay email truoc khi close
    cur.execute("SELECT Name, Email FROM Students WHERE StudentID=?", (borrow["StudentID"],))
    sv = cur.fetchone()
    conn.commit(); conn.close()

    # Gui email thong bao mo khoa
    if sv and sv["Email"]:
        try:
            from core.services.email_service import notify_card_unlocked
            _send_email_bg(notify_card_unlocked, sv["Email"], sv["Name"])
        except Exception as e:
            print(f"[Email] {e}")

    return True, "Da giai quyet xong. The doc gia duoc mo khoa."


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
        LIMIT 100
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

    fine_per_day = get_fine_per_day()
    cur.execute("""
        UPDATE Borrow 
        SET FineAmount = CAST((julianday(?) - julianday(DueDate)) * ? AS REAL)
        WHERE Status='Overdue' AND DueDate IS NOT NULL
    """, (today, fine_per_day))

    # Khoa the qua han > 30 ngay va gui email
    cur.execute("""
        SELECT b.StudentID, s.Name, s.Email,
               MAX(CAST(julianday(?) - julianday(b.DueDate) AS INTEGER)) as max_days,
               SUM(b.FineAmount) as total_fine
        FROM Borrow b JOIN Students s ON b.StudentID=s.StudentID
        WHERE b.Status='Overdue'
          AND CAST(julianday(?) - julianday(b.DueDate) AS INTEGER) > 30
          AND s.CardStatus != 'blocked'
        GROUP BY b.StudentID
    """, (today, today))
    to_block = cur.fetchall()
    for row in to_block:
        cur.execute("UPDATE Students SET CardStatus='blocked' WHERE StudentID=?", (row[0],))
        if row[2]:
            try:
                from core.services.email_service import notify_card_blocked
                _send_email_bg(notify_card_blocked,
                    row[2], row[1],
                    "Qua han tra sach tren 30 ngay", row[4] or 0)
            except Exception as e:
                print(f"[Email] {e}")

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
    cur.execute("SELECT COUNT(*) FROM Students WHERE CardStatus='blocked'")
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