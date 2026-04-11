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
                 phone="", email="", card_expire=""):
        self.student_id  = student_id
        self.name        = name
        self.faculty     = faculty
        self.class_      = class_
        self.phone       = phone
        self.email       = email
        self.card_expire = card_expire

class Staff:
    def __init__(self, staff_id="", name="", username="",
                 password="", role="staff"):
        self.staff_id = staff_id
        self.name     = name
        self.username = username
        self.password = password
        self.role     = role

class BorrowRecord:
    def __init__(self, borrow_id=None, student_id="", book_id="",
                 borrow_date="", due_date="", return_date=None,
                 status="Borrowing", fine_amount=0, fine_paid=False):
        self.borrow_id   = borrow_id
        self.student_id  = student_id
        self.book_id     = book_id
        self.borrow_date = borrow_date
        self.due_date    = due_date
        self.return_date = return_date
        self.status      = status
        self.fine_amount = fine_amount
        self.fine_paid   = fine_paid
