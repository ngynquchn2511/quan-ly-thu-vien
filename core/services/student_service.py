# CRUD sinh vien
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from database.models import Student


def get_all_students(keyword="", faculty=""):
    conn = get_connection()
    cur  = conn.cursor()
    sql  = "SELECT * FROM Students WHERE 1=1"
    p    = []
    if keyword:
        sql += " AND (Name LIKE ? OR StudentID LIKE ? OR Phone LIKE ?)"
        p   += [f"%{keyword}%"] * 3
    if faculty:
        sql += " AND Faculty=?"
        p.append(faculty)
    cur.execute(sql, p)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_student(student: Student):
    conn = get_connection()
    conn.execute("""
        INSERT INTO Students (StudentID,Name,Faculty,Class,Phone,Email,CardExpire)
        VALUES (?,?,?,?,?,?,?)
    """, (student.student_id, student.name, student.faculty,
          student.class_, student.phone, student.email, student.card_expire))
    conn.commit()
    conn.close()


def update_student(student: Student):
    conn = get_connection()
    conn.execute("""
        UPDATE Students SET Name=?,Faculty=?,Class=?,Phone=?,Email=?,CardExpire=?
        WHERE StudentID=?
    """, (student.name, student.faculty, student.class_,
          student.phone, student.email, student.card_expire, student.student_id))
    conn.commit()
    conn.close()


def delete_student(student_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM Students WHERE StudentID=?", (student_id,))
    conn.commit()
    conn.close()


def get_student_by_id(student_id: str):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM Students WHERE StudentID=?", (student_id,))
    row  = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_faculties():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT Faculty FROM Students WHERE Faculty IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
import hashlib

def authenticate_student(student_id, password):
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