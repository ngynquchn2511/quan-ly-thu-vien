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