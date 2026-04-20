# Dịch vụ Đánh giá sách
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from datetime import datetime


def get_reviews_by_book(book_id):
    """Lấy tất cả đánh giá của một cuốn sách."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, s.Name as StudentName
        FROM BookReviews r
        JOIN Students s ON r.StudentID = s.StudentID
        WHERE r.BookID = ?
        ORDER BY r.CreatedAt DESC
    """, (book_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_book_avg_rating(book_id):
    """Lấy điểm trung bình đánh giá của sách."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT AVG(Rating) as avg_rating, COUNT(*) as total
        FROM BookReviews WHERE BookID = ?
    """, (book_id,))
    row = cur.fetchone()
    conn.close()
    if row and row["total"] > 0:
        return round(row["avg_rating"], 1), row["total"]
    return 0, 0


def add_review(student_id, book_id, rating, comment=""):
    """Thêm đánh giá mới. Chỉ cho phép SV đã mượn và trả sách đó."""
    conn = get_connection()
    cur = conn.cursor()

    # Kiểm tra SV đã từng mượn và trả sách này chưa
    cur.execute("""
        SELECT COUNT(*) FROM Borrow
        WHERE StudentID=? AND BookID=? AND Status='Returned'
    """, (student_id, book_id))
    if cur.fetchone()[0] == 0:
        conn.close()
        return False, "Bạn chỉ được đánh giá sách đã mượn và trả."

    # Kiểm tra đã đánh giá chưa
    cur.execute("""
        SELECT COUNT(*) FROM BookReviews
        WHERE StudentID=? AND BookID=?
    """, (student_id, book_id))
    if cur.fetchone()[0] > 0:
        conn.close()
        return False, "Bạn đã đánh giá cuốn sách này rồi."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO BookReviews (StudentID, BookID, Rating, Comment, CreatedAt)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, book_id, rating, comment, now))
    conn.commit()
    conn.close()
    return True, "Đánh giá thành công!"


def delete_review(review_id):
    """Xóa đánh giá (dùng cho Admin kiểm duyệt)."""
    conn = get_connection()
    conn.execute("DELETE FROM BookReviews WHERE ReviewID=?", (review_id,))
    conn.commit()
    conn.close()
    return True
