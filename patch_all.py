"""
Chay script nay tu thu muc library-system:
    cd D:\BTL_Python\library-system
    python patch_all.py
"""
import os

files = {}

files["database/models.py"] = '''
class Book:
    def __init__(self, book_id="", title="", author="", category="",
                 publisher="", year=None, isbn="", quantity=1,
                 available=1, location=""):
        self.book_id   = book_id
        self.title     = title
        self.author    = author
        self.category  = category
        self.publisher = publisher
        self.year      = year
        self.isbn      = isbn
        self.quantity  = quantity
        self.available = available
        self.location  = location

class Student:
    def __init__(self, student_id="", name="", faculty="", class_="",
                 phone="", email="", card_expire=""):
        self.student_id  = student_id
        self.name        = name
        self.faculty     = faculty
        self.class_      = class_
        self.phone       = phone
        self.email       = email
        self.card_expire = card_expire

class Staff:
    def __init__(self, staff_id="", name="", username="",
                 password="", role="staff"):
        self.staff_id = staff_id
        self.name     = name
        self.username = username
        self.password = password
        self.role     = role

class BorrowRecord:
    def __init__(self, borrow_id=None, student_id="", book_id="",
                 borrow_date="", due_date="", return_date=None,
                 status="Borrowing", fine_amount=0, fine_paid=False):
        self.borrow_id   = borrow_id
        self.student_id  = student_id
        self.book_id     = book_id
        self.borrow_date = borrow_date
        self.due_date    = due_date
        self.return_date = return_date
        self.status      = status
        self.fine_amount = fine_amount
        self.fine_paid   = fine_paid
'''.lstrip()

files["database/db.py"] = '''
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    conn = get_connection()
    cur  = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS Books (
            BookID    TEXT PRIMARY KEY,
            Title     TEXT NOT NULL,
            Author    TEXT NOT NULL,
            Category  TEXT,
            Publisher TEXT,
            Year      INTEGER,
            ISBN      TEXT UNIQUE,
            Quantity  INTEGER DEFAULT 1,
            Available INTEGER DEFAULT 1,
            Location  TEXT
        );
        CREATE TABLE IF NOT EXISTS Students (
            StudentID  TEXT PRIMARY KEY,
            Name       TEXT NOT NULL,
            Faculty    TEXT,
            Class      TEXT,
            Phone      TEXT,
            Email      TEXT,
            CardExpire TEXT
        );
        CREATE TABLE IF NOT EXISTS Staff (
            StaffID  TEXT PRIMARY KEY,
            Name     TEXT NOT NULL,
            Username TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Role     TEXT DEFAULT 'staff'
        );
        CREATE TABLE IF NOT EXISTS Borrow (
            BorrowID   INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID  TEXT NOT NULL,
            BookID     TEXT NOT NULL,
            BorrowDate TEXT NOT NULL,
            DueDate    TEXT NOT NULL,
            ReturnDate TEXT,
            Status     TEXT DEFAULT 'Borrowing',
            FineAmount REAL DEFAULT 0,
            FinePaid   INTEGER DEFAULT 0,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (BookID)    REFERENCES Books(BookID)
        );
        CREATE TABLE IF NOT EXISTS FineRule (
            RuleID        INTEGER PRIMARY KEY AUTOINCREMENT,
            FeePerDay     REAL NOT NULL DEFAULT 2000,
            EffectiveDate TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS AuditLog (
            LogID     INTEGER PRIMARY KEY AUTOINCREMENT,
            StaffID   TEXT,
            Action    TEXT NOT NULL,
            TargetID  TEXT,
            Timestamp TEXT NOT NULL
        );
    """)
    import hashlib
    cur.execute("SELECT COUNT(*) FROM Staff WHERE Username=\'admin\'")
    if cur.fetchone()[0] == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute("""
            INSERT INTO Staff (StaffID,Name,Username,Password,Role)
            VALUES (\'NV001\',\'Quan Tri Vien\',\'admin\',?,\'admin\')
        """, (pw,))
    cur.execute("SELECT COUNT(*) FROM FineRule")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO FineRule (FeePerDay,EffectiveDate) VALUES (2000,\'2024-01-01\')")
    conn.commit()
    conn.close()
    print("[DB] Database initialized.")
'''.lstrip()

files["services/staff_service.py"] = '''
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from database.models import Staff

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def authenticate(username: str, password: str):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM Staff WHERE Username=?", (username,))
    row  = cur.fetchone()
    conn.close()
    if row and row["Password"] == hash_password(password):
        return dict(row)
    return None

def get_all_staff():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT StaffID,Name,Username,Role FROM Staff")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_staff(staff: Staff):
    conn = get_connection()
    conn.execute("""
        INSERT INTO Staff (StaffID,Name,Username,Password,Role)
        VALUES (?,?,?,?,?)
    """, (staff.staff_id, staff.name, staff.username,
          hash_password(staff.password), staff.role))
    conn.commit()
    conn.close()

def delete_staff(staff_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM Staff WHERE StaffID=?", (staff_id,))
    conn.commit()
    conn.close()
'''.lstrip()

files["gui/dashboard.py"] = '''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from config import APP_NAME

class DashboardWindow(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 680)
        lay = QVBoxLayout(self)
        name = self.current_user.get("Name", "")
        role = self.current_user.get("Role", "")
        lbl = QLabel(f"Xin chao, {name}  |  Quyen: {role}\\n\\n(Dashboard dang duoc xay dung...)")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #1A2540;")
        lay.addWidget(lbl)
'''.lstrip()

files["main.py"] = '''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from database.db import init_database
from gui.login_gui import LoginWindow

def main():
    init_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''.lstrip()

# Ghi tat ca file
for path, content in files.items():
    full = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {path}")

print("\nTat ca file da duoc cap nhat! Chay: python main.py")