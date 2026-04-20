# CRUD sach
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from database.models import Book


def get_all_books(keyword="", category=""):
    conn = get_connection()
    cur  = conn.cursor()
    sql  = "SELECT * FROM Books WHERE 1=1"
    p    = []
    if keyword:
        sql += " AND (Title LIKE ? OR Author LIKE ? OR ISBN LIKE ?)"
        p   += [f"%{keyword}%"] * 3
    if category:
        sql += " AND Category=?"
        p.append(category)
    cur.execute(sql, p)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_book(book: Book):
    conn = get_connection()
    conn.execute("""
        INSERT INTO Books (BookID,Title,Author,Category,Publisher,
                           Year,ISBN,Quantity,Available,Location)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (book.book_id, book.title, book.author, book.category,
          book.publisher, book.year, book.isbn,
          book.quantity, book.available, book.location))
    conn.commit()
    conn.close()


def update_book(book: Book):
    conn = get_connection()
    conn.execute("""
        UPDATE Books SET Title=?,Author=?,Category=?,Publisher=?,
        Year=?,ISBN=?,Quantity=?,Available=?,Location=?
        WHERE BookID=?
    """, (book.title, book.author, book.category, book.publisher,
          book.year, book.isbn, book.quantity, book.available,
          book.location, book.book_id))
    conn.commit()
    conn.close()


def delete_book(book_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM Books WHERE BookID=?", (book_id,))
    conn.commit()
    conn.close()


def get_book_by_id(book_id: str):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM Books WHERE BookID=?", (book_id,))
    row  = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_categories():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT Category FROM Books WHERE Category IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def search_books(keyword="", author="", category="", status="all"):
    """
    Search books with multiple criteria for Student Portal.
    """
    conn = get_connection()
    cur  = conn.cursor()
    sql  = "SELECT * FROM Books WHERE 1=1"
    p    = []
    
    if keyword:
        sql += " AND (Title LIKE ? OR ISBN LIKE ?)"
        p   += [f"%{keyword}%"] * 2
    if author:
        sql += " AND Author LIKE ?"
        p.append(f"%{author}%")
    if category:
        sql += " AND Category = ?"
        p.append(category)
    if status == "available":
        sql += " AND Available > 0"
    
    cur.execute(sql, p)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_new_books(limit=5):
    """Lấy sách mới nhập gần đây (theo BookID giảm dần)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM Books ORDER BY BookID DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_borrowed(limit=5):
    """Lấy sách mượn nhiều nhất."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT bk.*, COUNT(b.BorrowID) as BorrowCount
        FROM Books bk
        JOIN Borrow b ON bk.BookID = b.BookID
        GROUP BY bk.BookID
        ORDER BY BorrowCount DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recommended_books(student_id, limit=5):
    """Gợi ý sách dựa trên thể loại SV hay mượn."""
    conn = get_connection()
    cur = conn.cursor()
    # Tìm thể loại hay mượn nhất
    cur.execute("""
        SELECT bk.Category, COUNT(*) as cnt
        FROM Borrow b JOIN Books bk ON b.BookID = bk.BookID
        WHERE b.StudentID = ? AND bk.Category IS NOT NULL
        GROUP BY bk.Category ORDER BY cnt DESC LIMIT 3
    """, (student_id,))
    cats = [r[0] for r in cur.fetchall()]

    if not cats:
        # Chưa mượn gì thì gợi ý sách mượn nhiều
        cur.execute("""
            SELECT bk.* FROM Books bk
            JOIN Borrow b ON bk.BookID = b.BookID
            GROUP BY bk.BookID ORDER BY COUNT(*) DESC LIMIT ?
        """, (limit,))
    else:
        # Gợi ý sách cùng thể loại mà SV chưa mượn
        placeholders = ','.join('?' * len(cats))
        cur.execute(f"""
            SELECT * FROM Books
            WHERE Category IN ({placeholders})
            AND BookID NOT IN (
                SELECT BookID FROM Borrow WHERE StudentID = ?
            )
            ORDER BY Available DESC
            LIMIT ?
        """, (*cats, student_id, limit))

    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_favorite(student_id, book_id):
    """Bật/tắt yêu thích sách."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM Favorites
        WHERE StudentID=? AND BookID=?
    """, (student_id, book_id))
    exists = cur.fetchone()[0] > 0

    if exists:
        conn.execute("DELETE FROM Favorites WHERE StudentID=? AND BookID=?",
                     (student_id, book_id))
        conn.commit()
        conn.close()
        return False, "Đã bỏ yêu thích."
    else:
        conn.execute("INSERT INTO Favorites (StudentID, BookID) VALUES (?, ?)",
                     (student_id, book_id))
        conn.commit()
        conn.close()
        return True, "Đã thêm vào yêu thích."


def is_favorite(student_id, book_id):
    """Kiểm tra sách có trong danh sách yêu thích."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM Favorites
        WHERE StudentID=? AND BookID=?
    """, (student_id, book_id))
    result = cur.fetchone()[0] > 0
    conn.close()
    return result


def get_favorites(student_id):
    """Lấy danh sách sách yêu thích của SV."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT bk.* FROM Favorites f
        JOIN Books bk ON f.BookID = bk.BookID
        WHERE f.StudentID = ?
    """, (student_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]