import sqlite3
import sys
import os
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
    cur.execute("SELECT COUNT(*) FROM Staff WHERE Username='admin'")
    if cur.fetchone()[0] == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute("""
            INSERT INTO Staff (StaffID,Name,Username,Password,Role)
            VALUES ('NV001','Quan Tri Vien','admin',?,'admin')
        """, (pw,))
    cur.execute("SELECT COUNT(*) FROM FineRule")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO FineRule (FeePerDay,EffectiveDate) VALUES (2000,'2024-01-01')")
    conn.commit()
    conn.close()
    print("[DB] Database initialized.")
