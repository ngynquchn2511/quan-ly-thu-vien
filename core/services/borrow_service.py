# Logic muon/tra sach
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from datetime import datetime, timedelta
from core.config import DEFAULT_BORROW_DAYS, FINE_PER_DAY, MAX_BORROW_LIMIT


def borrow_book(student_id: str, book_id: str):
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT CardExpire FROM Students WHERE StudentID=?", (student_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Khong tim thay sinh vien."
    if row["CardExpire"] < datetime.now().strftime("%Y-%m-%d"):
        conn.close()
        return False, "The thu vien het han. Vui long gia han."

    cur.execute("SELECT COUNT(*) FROM Borrow WHERE StudentID=? AND Status='Borrowing'", (student_id,))
    if cur.fetchone()[0] >= MAX_BORROW_LIMIT:
        conn.close()
        return False, f"Dang muon toi da {MAX_BORROW_LIMIT} cuon."

    cur.execute("SELECT COUNT(*) FROM Borrow WHERE StudentID=? AND Status='Overdue'", (student_id,))
    if cur.fetchone()[0] > 0:
        conn.close()
        return False, "Con sach qua han chua tra."

    cur.execute("SELECT Available FROM Books WHERE BookID=?", (book_id,))
    book = cur.fetchone()
    if not book or book["Available"] <= 0:
        conn.close()
        return False, "Sach hien khong con trong kho."

    now = datetime.now()
    due = now + timedelta(days=DEFAULT_BORROW_DAYS)
    cur.execute("""
        INSERT INTO Borrow (StudentID,BookID,BorrowDate,DueDate,Status)
        VALUES (?,?,?,?,'Borrowing')
    """, (student_id, book_id,
          now.strftime("%Y-%m-%d"),
          due.strftime("%Y-%m-%d")))
    cur.execute("UPDATE Books SET Available=Available-1 WHERE BookID=?", (book_id,))
    conn.commit()
    conn.close()
    return True, f"Muon sach thanh cong. Han tra: {due.strftime('%d/%m/%Y')}."


def return_book(borrow_id: int):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM Borrow WHERE BorrowID=?", (borrow_id,))
    record = cur.fetchone()
    if not record:
        conn.close()
        return False, "Khong tim thay phieu muon.", 0

    today = datetime.now().date()
    due   = datetime.strptime(record["DueDate"], "%Y-%m-%d").date()
    fine  = max(0, (today - due).days) * FINE_PER_DAY if today > due else 0

    cur.execute("""
        UPDATE Borrow SET ReturnDate=?,Status='Returned',FineAmount=?
        WHERE BorrowID=?
    """, (today.strftime("%Y-%m-%d"), fine, borrow_id))
    cur.execute("UPDATE Books SET Available=Available+1 WHERE BookID=?", (record["BookID"],))
    conn.commit()
    conn.close()
    msg = f"Tra sach thanh cong. Tien phat: {fine:,.0f}d." if fine else "Tra sach thanh cong."
    return True, msg, fine


def get_active_borrows(keyword=""):
    conn = get_connection()
    cur  = conn.cursor()
    sql  = """
        SELECT b.BorrowID, b.StudentID, s.Name AS StudentName,
               bk.Title AS BookTitle, b.BorrowDate, b.DueDate, b.Status
        FROM Borrow b
        JOIN Students s ON b.StudentID=s.StudentID
        JOIN Books bk   ON b.BookID=bk.BookID
        WHERE b.Status IN ('Borrowing','Overdue')
    """
    p = []
    if keyword:
        sql += " AND (b.StudentID LIKE ? OR s.Name LIKE ? OR bk.Title LIKE ?)"
        p   += [f"%{keyword}%"] * 3
    sql += " ORDER BY b.DueDate ASC"
    cur.execute(sql, p)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_overdue_status():
    today = datetime.now().strftime("%Y-%m-%d")
    conn  = get_connection()
    conn.execute("""
        UPDATE Borrow SET Status='Overdue'
        WHERE Status='Borrowing' AND DueDate < ?
    """, (today,))
    conn.commit()
    conn.close()


def get_borrow_history(student_id=""):
    conn = get_connection()
    cur  = conn.cursor()
    sql  = """
        SELECT b.*, s.Name AS StudentName, bk.Title AS BookTitle
        FROM Borrow b
        JOIN Students s ON b.StudentID=s.StudentID
        JOIN Books bk   ON b.BookID=bk.BookID
    """
    p = []
    if student_id:
        sql += " WHERE b.StudentID=?"
        p.append(student_id)
    sql += " ORDER BY b.BorrowDate DESC"
    cur.execute(sql, p)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_stats():
    conn = get_connection()
    cur  = conn.cursor()
    stats = {}
    cur.execute("SELECT COUNT(*) FROM Books")
    stats["total_books"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Students")
    stats["total_students"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Borrow WHERE Status='Borrowing'")
    stats["borrowing"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Borrow WHERE Status='Overdue'")
    stats["overdue"] = cur.fetchone()[0]
    conn.close()
    return stats