class Book:
    def __init__(self, book_id="", title="", author="", category="",
                 publisher="", year=None, isbn="", quantity=1,
                 available=1, location=""):
        self.book_id   = book_id
        self.title     = title
        self.author    = author
        self.category  = category
        self.publisher = publisher
        self.year      = year
        self.isbn      = isbn
        self.quantity  = quantity
        self.available = available
        self.location  = location

class Student:
    def __init__(self, student_id="", name="", faculty="", class_="",
                 phone="", email="", card_expire="", password="",
                 password_hash="", card_status="active"):
        self.student_id    = student_id
        self.name          = name
        self.faculty       = faculty
        self.class_        = class_
        self.phone         = phone
        self.email         = email
        self.card_expire   = card_expire
        self.password      = password        # plaintext tạm (dùng khi tạo/đổi mật khẩu)
        self.password_hash = password_hash   # SHA-256 hash lưu trong DB
        self.card_status   = card_status     # 'active' | 'blocked'

    def is_card_valid(self):
        """Kiểm tra thẻ còn hiệu lực."""
        from datetime import datetime
        if self.card_status == "blocked":
            return False
        if self.card_expire:
            try:
                return datetime.strptime(self.card_expire, "%Y-%m-%d") >= datetime.now()
            except ValueError:
                return True
        return True

class Staff:
    def __init__(self, staff_id="", name="", username="",
                 password="", role="staff"):
        self.staff_id = staff_id
        self.name     = name
        self.username = username
        self.password = password
        self.role     = role

    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "StaffID":  self.staff_id,
            "Name":     self.name,
            "Username": self.username,
            "Role":     self.role,
        }

    def check_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == self.password

class BorrowRecord:
    def __init__(self, borrow_id=None, student_id="", book_id="",
                 borrow_date="", due_date="", return_date=None,
                 status="Borrowing", fine_amount=0, fine_paid=False,
                 renew_count=0, lost_date=None, staff_id="", rule_id=None):
        self.borrow_id   = borrow_id
        self.student_id  = student_id
        self.book_id     = book_id
        self.borrow_date = borrow_date
        self.due_date    = due_date
        self.return_date = return_date
        self.status      = status
        self.fine_amount = fine_amount
        self.fine_paid   = fine_paid
        self.renew_count = renew_count    # Số lần gia hạn (tối đa 1)
        self.lost_date   = lost_date      # Ngày đánh dấu mất sách
        self.staff_id    = staff_id       # Nhân viên xử lý
        self.rule_id     = rule_id        # Quy tắc phạt áp dụng

    def is_overdue(self):
        """Kiểm tra phiếu mượn đã quá hạn chưa."""
        from datetime import datetime
        if self.status != "Borrowing":
            return False
        if self.due_date:
            try:
                return datetime.strptime(self.due_date, "%Y-%m-%d") < datetime.now()
            except ValueError:
                return False
        return False
