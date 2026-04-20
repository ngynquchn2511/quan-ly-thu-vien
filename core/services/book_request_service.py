# Dịch vụ Đề xuất mua sách
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from datetime import datetime


def get_requests_by_student(student_id):
    """Lấy danh sách đề xuất của một sinh viên."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM BookRequests
        WHERE StudentID = ?
        ORDER BY CreatedAt DESC
    """, (student_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_requests(status_filter=""):
    """Lấy tất cả đề xuất (dùng cho Admin)."""
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT r.*, s.Name as StudentName
        FROM BookRequests r
        JOIN Students s ON r.StudentID = s.StudentID
    """
    params = []
    if status_filter:
        sql += " WHERE r.Status = ?"
        params.append(status_filter)
    sql += " ORDER BY r.CreatedAt DESC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_request(student_id, book_title, author="", reason=""):
    """Sinh viên gửi đề xuất mua sách mới."""
    if not book_title.strip():
        return False, "Vui lòng nhập tên sách."

    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO BookRequests (StudentID, BookTitle, Author, Reason, Status, CreatedAt)
        VALUES (?, ?, ?, ?, 'Pending', ?)
    """, (student_id, book_title.strip(), author.strip(), reason.strip(), now))
    conn.commit()
    conn.close()
    return True, "Đề xuất đã được gửi thành công!"


def update_request_status(request_id, status, admin_note=""):
    """Admin duyệt/từ chối đề xuất."""
    conn = get_connection()
    conn.execute("""
        UPDATE BookRequests SET Status=?, AdminNote=?
        WHERE RequestID=?
    """, (status, admin_note, request_id))
    conn.commit()
    conn.close()
    return True
