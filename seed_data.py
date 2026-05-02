"""
seed_data.py - Du lieu mau cho he thong thu vien
Chay 1 lan sau khi clone:
    python seed_data.py
"""
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_connection, init_database

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def seed():
    init_database()
    conn = get_connection()
    cur  = conn.cursor()

    # Them cot PasswordHash neu chua co
    cur.execute("PRAGMA table_info(Students)")
    cols = [row[1] for row in cur.fetchall()]
    if "PasswordHash" not in cols:
        cur.execute("ALTER TABLE Students ADD COLUMN PasswordHash TEXT")

    # ── Nhan vien ─────────────────────────────────────────────────────────────
    staffs = [
        ("NV001", "Quản Trị Viên",  "admin",   hash_pw("admin123"), "admin"),
        ("NV002", "Nguyễn Thị Hoa", "staff01", hash_pw("staff123"), "staff"),
        ("NV003", "Trần Văn Minh",  "staff02", hash_pw("staff123"), "staff"),
    ]
    for s in staffs:
        cur.execute("""
            INSERT OR IGNORE INTO Staff (StaffID,Name,Username,Password,Role)
            VALUES (?,?,?,?,?)
        """, s)

    # ── Sach ──────────────────────────────────────────────────────────────────
    books = [
        ("BK001","Lập trình Python cơ bản",       "Nguyễn Minh Nam",  "Lập trình","NXB ĐHQG",     2022,"978-604-1",  10,10,"A1-02"),
        ("BK002","Cơ sở dữ liệu phân tán",        "Trần Thị Thu",     "CNTT",     "NXB Bách Khoa",2021,"978-604-2",   5, 5,"B2-07"),
        ("BK003","Giải tích 1",                   "Lê Hoàng Phúc",    "Toán học", "NXB GD",       2020,"978-604-3",   8, 8,"C1-01"),
        ("BK004","Clean Code",                    "Robert C. Martin", "Lập trình","NXB Lao Động", 2019,"978-604-4",   4, 4,"A1-05"),
        ("BK005","Cấu trúc dữ liệu và giải thuật","Nguyễn Đức Nghĩa", "CNTT",     "NXB ĐHQG",     2021,"978-604-5",   6, 6,"A2-03"),
        ("BK006","Mạng máy tính",                 "Tanenbaum",        "CNTT",     "NXB Bách Khoa",2020,"978-604-6",   4, 4,"B1-04"),
        ("BK007","Triết học Mác-Lênin",           "Nguyễn Văn An",    "Đại cương","NXB CT QG",    2022,"978-604-7",  15,15,"D1-01"),
        ("BK008","Vật lý đại cương",              "Lương Duyên Bình", "Khoa học", "NXB GD",       2021,"978-604-8",   7, 7,"C2-02"),
        ("BK009","Tiếng Anh chuyên ngành IT",     "Smith J.",         "Ngoại ngữ","NXB ĐHQG",     2022,"978-604-9",   5, 5,"E1-01"),
        ("BK010","Kỹ thuật lập trình",            "Phạm Ngọc Hùng",   "Lập trình","NXB Bách Khoa",2023,"978-604-10",  4, 4,"A1-08"),
        ("BK011","Kinh tế vi mô",                 "Nguyễn Văn Dần",   "Kinh tế",  "NXB ĐH KTQD",  2021,"978-604-11", 6, 6,"F1-01"),
        ("BK012","Xác suất thống kê",             "Đặng Hùng Thắng",  "Toán học", "NXB GD",       2020,"978-604-12", 8, 8,"C1-03"),
    ]
    for b in books:
        cur.execute("""
            INSERT OR IGNORE INTO Books
            (BookID,Title,Author,Category,Publisher,Year,ISBN,Quantity,Available,Location)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, b)

    # ── Sinh vien (mat khau mac dinh = Ma SV) ────────────────────────────────
    students = [
        ("SV2021001","Nguyễn Văn Thành","CNTT",     "IT21A","0912345678","sv2021001@email.com","2026-12-31"),
        ("SV2021002","Lê Thị An",       "Kinh tế",  "KT21B","0987654321","sv2021002@email.com","2024-06-30"),
        ("SV2022001","Phạm Minh Khoa",  "CNTT",     "IT22C","0901122334","sv2022001@email.com","2027-12-31"),
        ("SV2022002","Trần Ngọc Linh",  "Cơ điện",  "CD22A","0909988776","sv2022002@email.com","2027-12-31"),
        ("SV2020001","Hoàng Đức Mạnh",  "CNTT",     "IT20B","0933445566","sv2020001@email.com","2025-12-31"),
        ("SV2023001","Vũ Thị Hoa",      "Ngoại ngữ","NN23A","0944556677","sv2023001@email.com","2028-12-31"),
        ("SV2021003","Đặng Văn Long",   "CNTT",     "IT21C","0955667788","sv2021003@email.com","2026-12-31"),
        ("SV2022003","Nguyễn Thị Mai",  "Kinh tế",  "KT22A","0966778899","sv2022003@email.com","2027-12-31"),
    ]
    for s in students:
        sid = s[0]
        cur.execute("""
            INSERT OR IGNORE INTO Students
            (StudentID,Name,Faculty,Class,Phone,Email,CardExpire,PasswordHash,ReaderType)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (*s, hash_pw(sid), "student"))  # Mat khau mac dinh = Ma SV

    # ── Giang vien (mat khau mac dinh = Ma GV) ───────────────────────────────
    lecturers = [
        ("GV001","TS. Nguyễn Hoài Nam", "CNTT",     "", "0903001001","gv001@univ.edu.vn","2028-12-31"),
        ("GV002","ThS. Trần Thu Hương", "Kinh tế",  "", "0903001002","gv002@univ.edu.vn","2027-12-31"),
        ("GV003","TS. Lê Minh Quân",    "Cơ điện",  "", "0903001003","gv003@univ.edu.vn","2028-06-30"),
        ("GV004","ThS. Phạm Ngọc Anh",  "Ngoại ngữ", "", "0903001004","gv004@univ.edu.vn","2029-12-31"),
    ]
    for l in lecturers:
        lid = l[0]
        cur.execute("""
            INSERT OR IGNORE INTO Students
            (StudentID,Name,Faculty,Class,Phone,Email,CardExpire,PasswordHash,ReaderType)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (*l, hash_pw(lid), "lecturer"))

    # ── Phieu muon mau ────────────────────────────────────────────────────────
    from datetime import datetime, timedelta
    today = datetime.now()
    borrows = [
        ("SV2021001","BK001",(today-timedelta(days=10)).strftime("%Y-%m-%d"),(today+timedelta(days=4)).strftime("%Y-%m-%d"), "Borrowing"),
        ("SV2021001","BK005",(today-timedelta(days=8)).strftime("%Y-%m-%d"), (today+timedelta(days=6)).strftime("%Y-%m-%d"), "Borrowing"),
        ("SV2021002","BK006",(today-timedelta(days=25)).strftime("%Y-%m-%d"),(today-timedelta(days=11)).strftime("%Y-%m-%d"),"Overdue"),
        ("SV2022001","BK003",(today-timedelta(days=12)).strftime("%Y-%m-%d"),(today+timedelta(days=2)).strftime("%Y-%m-%d"), "Borrowing"),
        ("SV2022002","BK002",(today-timedelta(days=23)).strftime("%Y-%m-%d"),(today-timedelta(days=9)).strftime("%Y-%m-%d"), "Overdue"),
        ("SV2020001","BK004",(today-timedelta(days=30)).strftime("%Y-%m-%d"),(today-timedelta(days=16)).strftime("%Y-%m-%d"),"Overdue"),
        ("SV2023001","BK007",(today-timedelta(days=5)).strftime("%Y-%m-%d"), (today+timedelta(days=9)).strftime("%Y-%m-%d"), "Borrowing"),
        ("SV2021003","BK009",(today-timedelta(days=3)).strftime("%Y-%m-%d"), (today+timedelta(days=11)).strftime("%Y-%m-%d"),"Borrowing"),
    ]
    for sid, bid, bdate, ddate, status in borrows:
        cur.execute("""
            INSERT OR IGNORE INTO Borrow (StudentID,BookID,BorrowDate,DueDate,Status)
            VALUES (?,?,?,?,?)
        """, (sid, bid, bdate, ddate, status))
        cur.execute(
            "UPDATE Books SET Available=Available-1 WHERE BookID=? AND Available>0", (bid,))
        if status == "Overdue":
            days = (today - datetime.strptime(ddate, "%Y-%m-%d")).days
            cur.execute(
                "UPDATE Borrow SET FineAmount=? WHERE StudentID=? AND BookID=? AND DueDate=?",
                (days * 2000, sid, bid, ddate))

    # ── Lich su tra mau ───────────────────────────────────────────────────────
    returned = [
        ("SV2021001","BK002",
         (today-timedelta(days=20)).strftime("%Y-%m-%d"),
         (today-timedelta(days=6)).strftime("%Y-%m-%d"),
         (today-timedelta(days=7)).strftime("%Y-%m-%d"), "Returned", 0, 0),
        ("SV2022001","BK001",
         (today-timedelta(days=15)).strftime("%Y-%m-%d"),
         (today-timedelta(days=1)).strftime("%Y-%m-%d"),
         (today-timedelta(days=2)).strftime("%Y-%m-%d"), "Returned", 0, 0),
    ]
    for r in returned:
        cur.execute("""
            INSERT OR IGNORE INTO Borrow
            (StudentID,BookID,BorrowDate,DueDate,ReturnDate,Status,FineAmount,FinePaid)
            VALUES (?,?,?,?,?,?,?,?)
        """, r)

    conn.commit()
    conn.close()

    print("=" * 55)
    print("SEED DATA HOÀN THÀNH!")
    print(f"  Nhân viên : {len(staffs)} tài khoản")
    print(f"  Sách      : {len(books)} quyển")
    print(f"  Sinh viên : {len(students)} người")
    print(f"  Giảng viên: {len(lecturers)} người")
    print(f"  Phiếu mượn: {len(borrows)} phiếu đang mượn")
    print(f"  Lịch sử   : {len(returned)} phiếu đã trả")
    print()
    print("Tài khoản đăng nhập Admin:")
    print("  admin  / admin123")
    print("  staff01 / staff123")
    print()
    print("Tài khoản sinh viên (mật khẩu mặc định = Mã SV):")
    for s in students:
        print(f"  {s[0]} / {s[0]}")
    print()
    print("Tài khoản giảng viên (mật khẩu mặc định = Mã GV):")
    for l in lecturers:
        print(f"  {l[0]} / {l[0]}")
    print("=" * 55)


if __name__ == "__main__":
    seed()