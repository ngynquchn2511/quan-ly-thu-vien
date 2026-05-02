import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import get_connection
from datetime import datetime


def init_messages_table():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Messages (
            MessageID  INTEGER PRIMARY KEY AUTOINCREMENT,
            SenderID   TEXT NOT NULL,
            SenderType TEXT NOT NULL,  -- 'staff' hoac 'student'
            ReceiverID TEXT NOT NULL,
            ReceiverType TEXT NOT NULL,
            Content    TEXT NOT NULL,
            SentAt     TEXT NOT NULL,
            IsRead     INTEGER DEFAULT 0
        )
    """)
    conn.commit(); conn.close()


def send_message(sender_id, sender_type, receiver_id, receiver_type, content):
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO Messages (SenderID, SenderType, ReceiverID, ReceiverType, Content, SentAt)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sender_id, sender_type, receiver_id, receiver_type, content, now))
    conn.commit(); conn.close()
    return True


def get_conversation(staff_id, student_id):
    """Lay lich su tin nhan giua 1 nhan vien va 1 sinh vien."""
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT m.*, 
               CASE WHEN m.SenderType='staff' THEN s.Name ELSE sv.Name END as SenderName
        FROM Messages m
        LEFT JOIN Staff s ON m.SenderID=s.StaffID AND m.SenderType='staff'
        LEFT JOIN Students sv ON m.SenderID=sv.StudentID AND m.SenderType='student'
        WHERE (m.SenderID=? AND m.ReceiverID=?)
           OR (m.SenderID=? AND m.ReceiverID=?)
        ORDER BY m.SentAt ASC
    """, (staff_id, student_id, student_id, staff_id))
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def mark_as_read(staff_id, student_id):
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Messages SET IsRead=1
        WHERE ReceiverID=? AND SenderID=? AND IsRead=0
    """, (staff_id, student_id))
    conn.commit(); conn.close()


def get_student_list_with_messages():
    """Lay danh sach sinh vien da nhan tin, kem tin nhan moi nhat."""
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT sv.StudentID, sv.Name, sv.Faculty, sv.Class,
               (SELECT Content FROM Messages
                WHERE (SenderID=sv.StudentID OR ReceiverID=sv.StudentID)
                ORDER BY SentAt DESC LIMIT 1) as LastMessage,
               (SELECT SentAt FROM Messages
                WHERE (SenderID=sv.StudentID OR ReceiverID=sv.StudentID)
                ORDER BY SentAt DESC LIMIT 1) as LastAt,
               (SELECT COUNT(*) FROM Messages
                WHERE ReceiverType='staff' AND SenderID=sv.StudentID
                AND IsRead=0) as UnreadCount
        FROM Students sv
        ORDER BY LastAt DESC NULLS LAST
    """)
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]


def get_unread_count(staff_id):
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM Messages
        WHERE ReceiverType='staff' AND IsRead=0
    """)
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_student_unread_count(student_id):
    """Dem tin nhan chua doc gui den sinh vien."""
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM Messages
        WHERE ReceiverID=? AND ReceiverType='student' AND IsRead=0
    """, (student_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count


def mark_student_read(student_id, staff_id):
    """Danh dau tin nhan gui den sinh vien tu 1 staff la da doc."""
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Messages SET IsRead=1
        WHERE ReceiverID=? AND SenderID=? AND ReceiverType='student' AND IsRead=0
    """, (student_id, staff_id))
    conn.commit(); conn.close()


def get_student_conversations(student_id):
    """Lay danh sach nhan vien da nhan tin voi sinh vien, kem tin nhan moi nhat."""
    init_messages_table()
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT
            CASE WHEN m.SenderType='staff' THEN m.SenderID ELSE m.ReceiverID END as StaffID
        FROM Messages m
        WHERE m.SenderID=? OR m.ReceiverID=?
    """, (student_id, student_id))
    staff_ids = [r[0] for r in cur.fetchall()]

    result = []
    for sid in staff_ids:
        cur.execute("SELECT StaffID, Name, Role FROM Staff WHERE StaffID=?", (sid,))
        staff_row = cur.fetchone()
        if not staff_row:
            continue
        # Tin nhan moi nhat
        cur.execute("""
            SELECT Content, SentAt FROM Messages
            WHERE (SenderID=? AND ReceiverID=?) OR (SenderID=? AND ReceiverID=?)
            ORDER BY SentAt DESC LIMIT 1
        """, (sid, student_id, student_id, sid))
        last = cur.fetchone()
        # Dem chua doc
        cur.execute("""
            SELECT COUNT(*) FROM Messages
            WHERE SenderID=? AND ReceiverID=? AND ReceiverType='student' AND IsRead=0
        """, (sid, student_id))
        unread = cur.fetchone()[0]

        result.append({
            "StaffID": staff_row["StaffID"],
            "Name": staff_row["Name"],
            "Role": staff_row["Role"],
            "LastMessage": last["Content"] if last else "",
            "LastAt": last["SentAt"] if last else "",
            "UnreadCount": unread,
        })

    conn.close()
    # Sap xep: chua doc truoc, roi theo thoi gian
    result.sort(key=lambda x: (-x["UnreadCount"], -(ord(x["LastAt"][0]) if x["LastAt"] else 0)))
    return result