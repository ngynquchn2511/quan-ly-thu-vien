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
            FinePaid   INTEGER DEFAULT 0,
            LostDate   TEXT,
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
            Timestamp TEXT NOT NULL,
            Detail    TEXT
        );
    """)

    # ── Migrate: them cot moi neu chua co ────────────────────────────────────
    migrations = [
        ("Students",  "PasswordHash", "TEXT"),
        ("Students",  "CardStatus",   "TEXT DEFAULT 'active'"),
        ("Books",     "Price",        "REAL DEFAULT 0"),
        ("Borrow",    "LostDate",     "TEXT"),
        ("AuditLog",  "Detail",       "TEXT"),
    ]
    for table, col, col_type in migrations:
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        if col not in cols:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")

    import hashlib

    # Tai khoan admin mac dinh
    cur.execute("SELECT COUNT(*) FROM Staff WHERE Username='admin'")
    if cur.fetchone()[0] == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute("""
            INSERT INTO Staff (StaffID,Name,Username,Password,Role)
            VALUES ('NV001','Quan Tri Vien','admin',?,'admin')
        """, (pw,))

    # FineRule mac dinh
    cur.execute("SELECT COUNT(*) FROM FineRule")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO FineRule (FeePerDay,EffectiveDate) VALUES (2000,'2024-01-01')")

    # Mat khau mac dinh cho sinh vien = Ma SV
    cur.execute(
        "SELECT StudentID FROM Students WHERE PasswordHash IS NULL OR PasswordHash=''")
    for (sid,) in cur.fetchall():
        pw = hashlib.sha256(sid.encode()).hexdigest()
        cur.execute(
            "UPDATE Students SET PasswordHash=? WHERE StudentID=?", (pw, sid))

    conn.commit()
    conn.close()
    print("[DB] Database initialized.")