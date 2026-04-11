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
