"""
Chay 1 lan de them cot PasswordHash vao bang Students:
    python add_student_password.py
"""
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_connection, init_database

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def migrate():
    init_database()
    conn = get_connection()
    cur  = conn.cursor()

    # Kiem tra cot da ton tai chua
    cur.execute("PRAGMA table_info(Students)")
    cols = [row[1] for row in cur.fetchall()]

    if "PasswordHash" not in cols:
        cur.execute("ALTER TABLE Students ADD COLUMN PasswordHash TEXT")
        print("[OK] Da them cot PasswordHash")
    else:
        print("[--] Cot PasswordHash da ton tai")

    # Set mat khau mac dinh = ma SV cho tat ca sinh vien chua co mat khau
    cur.execute("SELECT StudentID FROM Students WHERE PasswordHash IS NULL OR PasswordHash = ''")
    students = cur.fetchall()
    for (sid,) in students:
        cur.execute(
            "UPDATE Students SET PasswordHash=? WHERE StudentID=?",
            (hash_pw(sid), sid)
        )
        print(f"  [OK] {sid} -> mat khau mac dinh: {sid}")

    conn.commit()
    conn.close()
    print()
    print("HOAN THANH! Sinh vien dang nhap bang:")
    print("  Ma SV    : SV2021001")
    print("  Mat khau : SV2021001 (mac dinh)")

if __name__ == "__main__":
    migrate()