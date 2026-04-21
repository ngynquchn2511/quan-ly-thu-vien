import sqlite3
import sys
import os
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import DB_PATH

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
            Location  TEXT,
            Price     REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS Students (
            StudentID    TEXT PRIMARY KEY,
            Name         TEXT NOT NULL,
            Faculty      TEXT,
            Class        TEXT,
            Phone        TEXT,
            Email        TEXT,
            CardExpire   TEXT,
            PasswordHash TEXT,
            CardStatus   TEXT DEFAULT 'active'
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
            RenewCount INTEGER DEFAULT 0,
            StaffID    TEXT,
            RuleID     INTEGER,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (BookID)    REFERENCES Books(BookID),
            FOREIGN KEY (StaffID)   REFERENCES Staff(StaffID),
            FOREIGN KEY (RuleID)    REFERENCES FineRule(RuleID)
        );
        CREATE TABLE IF NOT EXISTS FineRule (
            RuleID        INTEGER PRIMARY KEY AUTOINCREMENT,
            FeePerDay     REAL NOT NULL DEFAULT 2000,
            EffectiveDate TEXT NOT NULL,
            StaffID       TEXT,
            FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
        );
        CREATE TABLE IF NOT EXISTS AuditLog (
            LogID     INTEGER PRIMARY KEY AUTOINCREMENT,
            StaffID   TEXT,
            Action    TEXT NOT NULL,
            TargetID  TEXT,
            Timestamp TEXT NOT NULL,
            Detail    TEXT,
            FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
        );
        CREATE TABLE IF NOT EXISTS Announcements (
            AnnouncementID INTEGER PRIMARY KEY AUTOINCREMENT,
            StaffID        TEXT,
            Title          TEXT NOT NULL,
            Content        TEXT,
            CreatedAt      TEXT NOT NULL,
            IsImportant    INTEGER DEFAULT 0,
            RelatedBookID  TEXT,
            FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
            FOREIGN KEY (RelatedBookID) REFERENCES Books(BookID)
        );
        CREATE TABLE IF NOT EXISTS BookReviews (
            ReviewID   INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID  TEXT NOT NULL,
            BookID     TEXT NOT NULL,
            BorrowID   INTEGER,
            Rating     INTEGER NOT NULL CHECK(Rating BETWEEN 1 AND 5),
            Comment    TEXT,
            CreatedAt  TEXT NOT NULL,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (BookID)    REFERENCES Books(BookID),
            FOREIGN KEY (BorrowID)  REFERENCES Borrow(BorrowID)
        );
        CREATE TABLE IF NOT EXISTS BookRequests (
            RequestID  INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID  TEXT NOT NULL,
            BookTitle  TEXT NOT NULL,
            Author     TEXT,
            Reason     TEXT,
            Status     TEXT DEFAULT 'Pending',
            AdminNote  TEXT,
            CreatedAt  TEXT NOT NULL,
            StaffID    TEXT,
            AcquiredBookID TEXT,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (StaffID)   REFERENCES Staff(StaffID),
            FOREIGN KEY (AcquiredBookID) REFERENCES Books(BookID)
        );
        CREATE TABLE IF NOT EXISTS Favorites (
            StudentID TEXT NOT NULL,
            BookID    TEXT NOT NULL,
            PRIMARY KEY (StudentID, BookID),
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (BookID)    REFERENCES Books(BookID)
        );
    """)

    # ── Migration: ensure new columns exist ────────────────────────────────
    migrations = [
        ("Students",  "PasswordHash", "TEXT"),
        ("Students",  "CardStatus",   "TEXT DEFAULT 'active'"),
        ("Books",     "Price",        "REAL DEFAULT 0"),
        ("Borrow",    "LostDate",     "TEXT"),
        ("Borrow",    "RenewCount",   "INTEGER DEFAULT 0"),
        ("AuditLog",  "Detail",       "TEXT"),
        ("Announcements", "StaffID",  "TEXT"),
        ("Borrow",        "StaffID",  "TEXT"),
        ("FineRule",      "StaffID",  "TEXT"),
        ("BookRequests",  "StaffID",  "TEXT"),
        ("Borrow",        "RuleID",   "INTEGER"),
        ("BookReviews",   "BorrowID", "INTEGER"),
        ("BookRequests",  "AcquiredBookID", "TEXT"),
        ("Announcements", "RelatedBookID", "TEXT")
    ]
    for table, col, col_type in migrations:
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        if col not in cols:
            try:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            except Exception as e:
                print(f"[DB] Migration error on {table}.{col}: {e}")

    # ── Default Admin ──────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM Staff WHERE Username='admin'")
    if cur.fetchone()[0] == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute("""
            INSERT INTO Staff (StaffID, Name, Username, Password, Role)
            VALUES ('NV001', 'Quan Tri Vien', 'admin', ?, 'admin')
        """, (pw,))

    # ── Sample Students ────────────────────────────────────────────────────
    sample_students = [
        ('SV001', 'Sinh Vien Mau', 'CNTT', 'K65', '0123456789', 'sv@gmail.com', '2025-01-01'),
        ('SV002', 'Nguyen Van B', 'Kinh tế', 'K64', '0987654321', 'sv2@gmail.com', '2025-06-01')
    ]
    for sid, name, fac, cls, ph, em, exp in sample_students:
        cur.execute("SELECT COUNT(*) FROM Students WHERE StudentID=?", (sid,))
        if cur.fetchone()[0] == 0:
            pw_hash = hashlib.sha256(sid.encode()).hexdigest()
            cur.execute("""
                INSERT INTO Students (StudentID, Name, Faculty, Class, Phone, Email, CardExpire, PasswordHash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, name, fac, cls, ph, em, exp, pw_hash))

    # ── FineRules ──────────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM FineRule")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO FineRule (FeePerDay, EffectiveDate) VALUES (2000, '2024-01-01')")
    
    # ── Sample Books ───────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM Books")
    if cur.fetchone()[0] == 0:
        books = [
            ('B001', 'Deep Learning', 'Ian Goodfellow', 'Công nghệ thông tin', 'MIT Press', 2016, '9780262035613', 5, 5, 'Kệ A1'),
            ('B002', 'Clean Architecture', 'Robert C. Martin', 'Công nghệ thông tin', 'Prentice Hall', 2017, '9780134494166', 3, 3, 'Kệ A2'),
            ('B003', 'Design Patterns', 'Erich Gamma', 'Công nghệ thông tin', 'Addison-Wesley', 1994, '9780201633610', 2, 2, 'Kệ A1'),
            ('B004', 'Thinking, Fast and Slow', 'Daniel Kahneman', 'Tâm lý học', 'Farrar, Straus and Giroux', 2011, '9780374275631', 4, 4, 'Kệ B1'),
            ('B005', 'The Lean Startup', 'Eric Ries', 'Kinh tế', 'Crown Business', 2011, '9780307887894', 6, 6, 'Kệ C1')
        ]
        cur.executemany("""
            INSERT INTO Books (BookID, Title, Author, Category, Publisher, Year, ISBN, Quantity, Available, Location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, books)

    conn.commit()
    conn.close()
    print("[DB] Database initialized.")

if __name__ == "__main__":
    init_database()