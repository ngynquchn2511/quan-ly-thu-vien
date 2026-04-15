import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from config import FINE_PER_DAY
from datetime import datetime


def get_overdue_list():
    conn  = get_connection()
    cur   = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT b.BorrowID, b.StudentID, s.Name, bk.Title,
               b.DueDate, b.FineAmount, b.FinePaid,
               CAST(julianday(?) - julianday(b.DueDate) AS INTEGER) AS OverdueDays
        FROM Borrow b
        JOIN Students s ON b.StudentID=s.StudentID
        JOIN Books bk   ON b.BookID=bk.BookID
        WHERE b.Status='Overdue'
        ORDER BY b.DueDate ASC
    """, (today,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_fine_paid(borrow_id: int):
    conn = get_connection()
    conn.execute("UPDATE Borrow SET FinePaid=1 WHERE BorrowID=?", (borrow_id,))
    conn.commit()
    conn.close()


def calculate_fine(due_date_str: str) -> float:
    due   = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    days  = (today - due).days
    return max(0, days * FINE_PER_DAY)