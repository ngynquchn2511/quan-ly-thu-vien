# Dịch vụ Thông báo
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from datetime import datetime


def get_announcements(limit=20):
    """Lấy danh sách thông báo mới nhất."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM Announcements
        ORDER BY CreatedAt DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_announcements(limit=5):
    """Lấy thông báo gần đây cho trang chủ."""
    return get_announcements(limit)


def get_announcement_count():
    """Đếm tổng số thông báo."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Announcements")
    count = cur.fetchone()[0]
    conn.close()
    return count


def add_announcement(title, content, is_important=0, staff_id=None):
    """Thêm thông báo mới (dùng cho Admin)."""
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO Announcements (Title, Content, CreatedAt, IsImportant, StaffID)
        VALUES (?, ?, ?, ?, ?)
    """, (title, content, now, is_important, staff_id))
    conn.commit()
    conn.close()
    return True


def delete_announcement(announcement_id):
    """Xóa thông báo (dùng cho Admin)."""
    conn = get_connection()
    conn.execute("DELETE FROM Announcements WHERE AnnouncementID=?",
                 (announcement_id,))
    conn.commit()
    conn.close()
    return True
