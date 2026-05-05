import smtplib
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database.db import get_connection

# Cau hinh Gmail
GMAIL_USER = "hoanquoc2511@gmail.com"
GMAIL_PASS = "colk fgvo ozen odob"


def send_email(to_email, subject, body_html):
    """Gui email den mot dia chi cu the."""
    if not to_email or "@" not in to_email:
        print(f"[Email] Bo qua - email khong hop le: {to_email}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Thu vien EAUT <{GMAIL_USER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(body_html, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_USER, GMAIL_PASS)
            s.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[Email] Da gui den {to_email}")
        return True
    except Exception as e:
        print(f"[Email] Loi khi gui den {to_email}: {e}")
        return False


def _html_template(title, greeting, body, color="#378ADD"):
    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;margin:0 auto;background:#F8FAFC;border-radius:12px;overflow:hidden">
      <div style="background:{color};padding:24px 32px">
        <h2 style="color:white;margin:0;font-size:20px">📚 Thư viện EAUT</h2>
      </div>
      <div style="padding:28px 32px;background:white">
        <p style="color:#1E293B;font-size:16px;margin:0 0 16px">{greeting}</p>
        {body}
        <hr style="border:none;border-top:1px solid #E2E8F0;margin:24px 0">
        <p style="color:#94A3B8;font-size:13px;margin:0">Email tự động từ hệ thống thư viện. Vui lòng không reply.</p>
      </div>
    </div>"""


def notify_announcement(student_email, student_name, title, content, is_important=False):
    """Gui thong bao chung den sinh vien."""
    icon  = "🔴" if is_important else "📢"
    color = "#EF4444" if is_important else "#378ADD"
    body  = f"""
        <div style="background:#F1F5F9;border-left:4px solid {color};padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0">
          <h3 style="color:#1E293B;margin:0 0 8px">{icon} {title}</h3>
          <p style="color:#475569;margin:0;line-height:1.6">{content or 'Không có nội dung chi tiết.'}</p>
        </div>
        <p style="color:#475569">Vui lòng liên hệ thư viện nếu có thắc mắc.</p>"""
    html = _html_template(
        title, f"Xin chào <b>{student_name}</b>,", body, color)
    return send_email(student_email,
                      f"{'[QUAN TRỌNG] ' if is_important else ''}Thông báo thư viện: {title}",
                      html)


def notify_card_blocked(student_email, student_name, reason, fine_amount=0):
    """Thong bao the bi khoa."""
    fine_text = f"<p style='color:#EF4444;font-weight:600'>💰 Tiền phạt: {fine_amount:,.0f}đ</p>" if fine_amount > 0 else ""
    body = f"""
        <div style="background:#FEF2F2;border-left:4px solid #EF4444;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0">
          <h3 style="color:#991B1B;margin:0 0 8px">🔒 Thẻ thư viện của bạn đã bị KHÓA</h3>
          <p style="color:#7F1D1D;margin:0"><b>Lý do:</b> {reason}</p>
        </div>
        {fine_text}
        <p style="color:#475569">Để mở khóa thẻ, vui lòng đến thư viện xử lý trực tiếp với thủ thư.</p>"""
    html = _html_template(
        "Thẻ bị khóa", f"Xin chào <b>{student_name}</b>,", body, "#EF4444")
    return send_email(student_email,
                      "⚠ Thẻ thư viện của bạn đã bị khóa",
                      html)


def notify_card_unlocked(student_email, student_name):
    """Thong bao the duoc mo khoa."""
    body = f"""
        <div style="background:#F0FDF4;border-left:4px solid #22C55E;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0">
          <h3 style="color:#166534;margin:0 0 8px">🔓 Thẻ thư viện của bạn đã được MỞ KHÓA</h3>
          <p style="color:#14532D;margin:0">Bạn có thể tiếp tục sử dụng dịch vụ mượn sách bình thường.</p>
        </div>
        <p style="color:#475569">Cảm ơn bạn đã hoàn thành nghĩa vụ với thư viện. Hãy mượn sách đúng hạn nhé!</p>"""
    html = _html_template(
        "Thẻ được mở khóa", f"Xin chào <b>{student_name}</b>,", body, "#22C55E")
    return send_email(student_email,
                      "✅ Thẻ thư viện của bạn đã được mở khóa",
                      html)


def notify_overdue(student_email, student_name, book_title, days_overdue, fine_amount):
    """Thong bao sach qua han."""
    body = f"""
        <div style="background:#FFFBEB;border-left:4px solid #F59E0B;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0">
          <h3 style="color:#92400E;margin:0 0 8px">⏰ Sách quá hạn trả</h3>
          <p style="color:#78350F;margin:4px 0"><b>Sách:</b> {book_title}</p>
          <p style="color:#78350F;margin:4px 0"><b>Số ngày quá hạn:</b> {days_overdue} ngày</p>
          <p style="color:#EF4444;margin:4px 0;font-weight:600"><b>Tiền phạt hiện tại:</b> {fine_amount:,.0f}đ</p>
        </div>
        <p style="color:#475569">Vui lòng đến thư viện trả sách sớm để tránh tăng thêm tiền phạt.</p>
        <p style="color:#EF4444;font-size:13px">⚠ Nếu quá hạn 30 ngày, thẻ thư viện sẽ bị khóa tự động.</p>"""
    html = _html_template(
        "Sách quá hạn", f"Xin chào <b>{student_name}</b>,", body, "#F59E0B")
    return send_email(student_email,
                      f"⏰ Nhắc nhở: Sách '{book_title}' đã quá hạn {days_overdue} ngày",
                      html)


def broadcast_announcement(title, content, is_important=False):
    """Gui thong bao den TAT CA sinh vien co email."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT StudentID, Name, Email FROM Students WHERE Email IS NOT NULL AND Email != ''")
    students = cur.fetchall(); conn.close()
    ok_count = 0
    for s in students:
        if notify_announcement(s["Email"], s["Name"], title, content, is_important):
            ok_count += 1
    print(f"[Email] Broadcast xong: {ok_count}/{len(students)} thanh cong")
    return ok_count