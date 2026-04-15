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