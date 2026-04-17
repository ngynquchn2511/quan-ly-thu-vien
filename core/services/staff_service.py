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


    # Them ham nay vao cuoi file core/services/student_service.py

import hashlib

def authenticate_student(student_id, password):
    """
    Xac thuc sinh vien.
    Tra ve dict thong tin sinh vien neu dung, None neu sai.
    """
    from database.db import get_connection
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT StudentID, Name, Faculty, Class, Phone, Email, CardExpire
        FROM Students
        WHERE StudentID=? AND PasswordHash=?
    """, (student_id, pw_hash))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "StudentID":  row[0],
            "Name":       row[1],
            "Faculty":    row[2],
            "Class":      row[3],
            "Phone":      row[4],
            "Email":      row[5],
            "CardExpire": row[6],
        }
    return None


def change_student_password(student_id, old_password, new_password):
    """
    Doi mat khau sinh vien.
    Tra ve (True, "Thanh cong") hoac (False, "Ly do loi")
    """
    from database.db import get_connection
    if authenticate_student(student_id, old_password) is None:
        return False, "Mật khẩu cũ không đúng."
    if len(new_password) < 6:
        return False, "Mật khẩu mới phải có ít nhất 6 ký tự."
    pw_hash = hashlib.sha256(new_password.encode()).hexdigest()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE Students SET PasswordHash=? WHERE StudentID=?",
        (pw_hash, student_id))
    conn.commit()
    conn.close()
    return True, "Đổi mật khẩu thành công."