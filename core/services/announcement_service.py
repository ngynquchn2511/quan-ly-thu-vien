import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import get_connection
from datetime import datetime


def get_recent_announcements(limit=4):
    """Lay thong bao moi nhat (dung cho trang chu user)."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT a.AnnouncementID, a.Title, a.Content, a.CreatedAt,
               a.IsImportant, a.RelatedBookID,
               s.Name as StaffName
        FROM Announcements a
        LEFT JOIN Staff s ON a.StaffID = s.StaffID
        ORDER BY a.IsImportant DESC, a.CreatedAt DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def get_announcements(limit=20):
    """Lay danh sach thong bao (dung cho trang thong bao user)."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT a.AnnouncementID, a.Title, a.Content, a.CreatedAt,
               a.IsImportant, a.RelatedBookID,
               s.Name as StaffName
        FROM Announcements a
        LEFT JOIN Staff s ON a.StaffID = s.StaffID
        ORDER BY a.IsImportant DESC, a.CreatedAt DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def get_announcement_count():
    """Dem so thong bao (dung cho badge chuong user)."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Announcements")
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_all_announcements(keyword=""):
    conn = get_connection(); cur = conn.cursor()
    kw = f"%{keyword}%"
    cur.execute("""
        SELECT a.AnnouncementID, a.Title, a.Content, a.CreatedAt,
               a.IsImportant, a.RelatedBookID,
               s.Name as StaffName, b.Title as BookTitle
        FROM Announcements a
        LEFT JOIN Staff s ON a.StaffID = s.StaffID
        LEFT JOIN Books b ON a.RelatedBookID = b.BookID
        WHERE a.Title LIKE ? OR a.Content LIKE ?
        ORDER BY a.IsImportant DESC, a.CreatedAt DESC
    """, (kw, kw))
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def add_announcement(title, content, staff_id, related_book_id=None, is_important=0):
    conn = get_connection(); cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO Announcements (StaffID, RelatedBookID, Title, Content, CreatedAt, IsImportant)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (staff_id, related_book_id or None, title, content, now, is_important))
    conn.commit(); conn.close()
    return True, "Đã thêm thông báo thành công."


def update_announcement(ann_id, title, content, related_book_id=None, is_important=0):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Announcements
        SET Title=?, Content=?, RelatedBookID=?, IsImportant=?
        WHERE AnnouncementID=?
    """, (title, content, related_book_id or None, is_important, ann_id))
    conn.commit(); conn.close()
    return True, "Đã cập nhật thông báo."


def delete_announcement(ann_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Announcements WHERE AnnouncementID=?", (ann_id,))
    conn.commit(); conn.close()
    return True, "Đã xóa thông báo."


def get_book_requests(keyword="", status=""):
    conn = get_connection(); cur = conn.cursor()
    kw = f"%{keyword}%"
    q = """
        SELECT r.RequestID, r.StudentID, s.Name as StudentName,
               r.BookTitle, r.Author, r.Reason, r.Status,
               r.AdminNote, r.CreatedAt, r.AcquiredBookID
        FROM BookRequests r
        JOIN Students s ON r.StudentID = s.StudentID
        WHERE (r.BookTitle LIKE ? OR s.Name LIKE ?)
    """
    params = [kw, kw]
    if status and status != "Tất cả":
        STATUS_MAP = {"Chờ duyệt": "Pending", "Đã duyệt": "Approved",
                      "Từ chối": "Rejected", "Đã mua": "Acquired"}
        q += " AND r.Status = ?"
        params.append(STATUS_MAP.get(status, status))
    q += " ORDER BY r.CreatedAt DESC"
    cur.execute(q, params)
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def update_request_status(request_id, status, admin_note, staff_id, acquired_book_id=None):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE BookRequests
        SET Status=?, AdminNote=?, StaffID=?, AcquiredBookID=?
        WHERE RequestID=?
    """, (status, admin_note, staff_id, acquired_book_id or None, request_id))
    conn.commit(); conn.close()
    return True, "Đã cập nhật yêu cầu."


def get_book_reviews(book_id=None, keyword=""):
    conn = get_connection(); cur = conn.cursor()
    kw = f"%{keyword}%"
    if book_id:
        cur.execute("""
            SELECT r.ReviewID, r.BookID, b.Title as BookTitle,
                   r.StudentID, s.Name as StudentName,
                   r.Rating, r.Comment, r.CreatedAt
            FROM BookReviews r
            JOIN Books b ON r.BookID = b.BookID
            JOIN Students s ON r.StudentID = s.StudentID
            WHERE r.BookID = ?
            ORDER BY r.CreatedAt DESC
        """, (book_id,))
    else:
        cur.execute("""
            SELECT r.ReviewID, r.BookID, b.Title as BookTitle,
                   r.StudentID, s.Name as StudentName,
                   r.Rating, r.Comment, r.CreatedAt
            FROM BookReviews r
            JOIN Books b ON r.BookID = b.BookID
            JOIN Students s ON r.StudentID = s.StudentID
            WHERE b.Title LIKE ? OR s.Name LIKE ?
            ORDER BY r.CreatedAt DESC
        """, (kw, kw))
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def delete_review(review_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM BookReviews WHERE ReviewID=?", (review_id,))
    conn.commit(); conn.close()
    return True, "Đã xóa đánh giá."


def get_favorites_by_category():
    """Lay sach duoc yeu thich nhieu nhat cua tung the loai, sap xep giam dan."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT b.Category,
               b.BookID, b.Title, b.Author,
               COUNT(f.BookID) as FavoriteCount,
               AVG(r.Rating) as AvgRating
        FROM Favorites f
        JOIN Books b ON f.BookID = b.BookID
        LEFT JOIN BookReviews r ON b.BookID = r.BookID
        GROUP BY b.BookID
        ORDER BY b.Category ASC, FavoriteCount DESC
    """)
    rows = cur.fetchall(); conn.close()

    # Nhom theo the loai, chi lay top 1 moi the loai
    result = {}
    for r in rows:
        cat = r["Category"] or "Khác"
        if cat not in result:
            result[cat] = dict(r)

    # Tra ve danh sach tat ca sach yeu thich co so luong giam dan
    cur2 = get_connection().cursor()
    conn2 = get_connection()
    cur2 = conn2.cursor()
    cur2.execute("""
        SELECT b.Category,
               b.BookID, b.Title, b.Author,
               COUNT(f.BookID) as FavoriteCount,
               ROUND(AVG(r.Rating), 1) as AvgRating
        FROM Favorites f
        JOIN Books b ON f.BookID = b.BookID
        LEFT JOIN BookReviews r ON b.BookID = r.BookID
        GROUP BY b.BookID
        ORDER BY b.Category ASC, FavoriteCount DESC
    """)
    all_rows = cur2.fetchall(); conn2.close()
    return [dict(r) for r in all_rows]