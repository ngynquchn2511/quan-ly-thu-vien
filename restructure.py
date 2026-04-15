"""
Chay tu thu muc library-system:
    python restructure.py

Script nay se:
1. Tao cay thu muc moi chuan
2. Di chuyen cac file vao dung vi tri
3. Cap nhat import trong tung file
"""
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Tao thu muc moi ───────────────────────────────────────────────────────────
dirs = [
    "admin_app/gui",
    "user_app/gui",
    "core/services",
    "core/utils",
    "database",
    "reports",
]
for d in dirs:
    os.makedirs(os.path.join(BASE, d), exist_ok=True)
    init = os.path.join(BASE, d, "__init__.py")
    if not os.path.exists(init):
        open(init, "w").close()
print("[1] Tao thu muc xong")

# ── Di chuyen file ────────────────────────────────────────────────────────────
moves = [
    # (nguon, dich)
    # Admin GUI
    ("gui/login_gui.py",    "admin_app/gui/login_gui.py"),
    ("gui/dashboard.py",    "admin_app/gui/dashboard.py"),
    ("gui/book_gui.py",     "admin_app/gui/book_gui.py"),
    ("gui/student_gui.py",  "admin_app/gui/student_gui.py"),
    ("gui/borrow_gui.py",   "admin_app/gui/borrow_gui.py"),
    ("gui/staff_gui.py",    "admin_app/gui/staff_gui.py"),
    ("gui/reports_gui.py",  "admin_app/gui/reports_gui.py"),
    # Admin main
    ("main.py",             "admin_app/main.py"),
    # Core services
    ("services/book_service.py",    "core/services/book_service.py"),
    ("services/student_service.py", "core/services/student_service.py"),
    ("services/borrow_service.py",  "core/services/borrow_service.py"),
    ("services/fine_service.py",    "core/services/fine_service.py"),
    ("services/staff_service.py",   "core/services/staff_service.py"),
    # Core utils
    ("utils/helpers.py",    "core/utils/helpers.py"),
    ("utils/validators.py", "core/utils/validators.py"),
    # Core config & styles
    ("config.py",           "core/config.py"),
    ("styles.py",           "core/styles.py"),
    # Database
    ("database/db.py",      "database/db.py"),
    ("database/models.py",  "database/models.py"),
    # Reports
    ("reports/export_excel.py", "reports/export_excel.py"),
]

for src, dst in moves:
    src_full = os.path.join(BASE, src)
    dst_full = os.path.join(BASE, dst)
    if os.path.exists(src_full):
        os.makedirs(os.path.dirname(dst_full), exist_ok=True)
        shutil.copy2(src_full, dst_full)
        print(f"  [OK] {src} -> {dst}")
    else:
        print(f"  [--] Bo qua (khong ton tai): {src}")

print("[2] Di chuyen file xong")

# ── Tao user_app placeholder ──────────────────────────────────────────────────
user_files = {
    "user_app/main.py": '''import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from database.db import init_database
from user_app.gui.login_gui import LoginWindow
import core.styles as styles

def main():
    init_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 14))
    app.setStyleSheet(styles.APP_STYLE)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
''',
    "user_app/gui/__init__.py": "",
    "user_app/gui/login_gui.py": '''# Trang dang nhap cho sinh vien
# TODO: Sinh vien chi dang nhap bang ma SV
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thu Vien - Sinh Vien")
        self.resize(400, 300)
        lay = QVBoxLayout(self)
        lbl = QLabel("Man hinh dang nhap sinh vien\\n(Dang xay dung...)")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
''',
    "user_app/gui/home_gui.py": '''# Trang chu - Tim kiem sach
# TODO: Hien thi sach co san, tim kiem
from PyQt5.QtWidgets import QWidget
class HomeWindow(QWidget):
    pass
''',
    "user_app/gui/my_books_gui.py": '''# Sach dang muon cua sinh vien
# TODO: Hien thi danh sach sach dang muon, qua han
from PyQt5.QtWidgets import QWidget
class MyBooksWindow(QWidget):
    pass
''',
    "user_app/gui/search_gui.py": '''# Tim kiem sach
# TODO: Tim kiem theo ten, tac gia, the loai
from PyQt5.QtWidgets import QWidget
class SearchWindow(QWidget):
    pass
''',
    "user_app/gui/profile_gui.py": '''# Thong tin ca nhan sinh vien
# TODO: Hien thi thong tin, lich su muon sach
from PyQt5.QtWidgets import QWidget
class ProfileWindow(QWidget):
    pass
''',
}

for path, content in user_files.items():
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if not os.path.exists(full):
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [NEW] {path}")

print("[3] Tao user_app placeholder xong")

# ── Tao admin_app/main.py moi ─────────────────────────────────────────────────
admin_main = '''import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from database.db import init_database
from admin_app.gui.login_gui import LoginWindow
import core.styles as styles

def main():
    init_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 14))
    app.setStyleSheet(styles.APP_STYLE)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''
with open(os.path.join(BASE, "admin_app/main.py"), "w", encoding="utf-8") as f:
    f.write(admin_main)
print("[4] Tao admin_app/main.py xong")

# ── Tao root main.py de chon app ──────────────────────────────────────────────
root_main = '''"""
ENTRY POINT CHINH
Chay admin: python main.py admin
Chay user:  python main.py user
"""
import sys

if len(sys.argv) < 2:
    print("Dung: python main.py [admin|user]")
    print("  admin - Ung dung quan tri thu vien")
    print("  user  - Ung dung danh cho sinh vien")
    sys.exit(1)

if sys.argv[1] == "admin":
    from admin_app.main import main
elif sys.argv[1] == "user":
    from user_app.main import main
else:
    print(f"Khong biet app: {sys.argv[1]}")
    sys.exit(1)

main()
'''
with open(os.path.join(BASE, "main.py"), "w", encoding="utf-8") as f:
    f.write(root_main)
print("[5] Tao root main.py xong")

# ── Tao .gitignore ────────────────────────────────────────────────────────────
gitignore = """__pycache__/
*.pyc
*.db
*.xlsx
.env
*.log
"""
with open(os.path.join(BASE, ".gitignore"), "w") as f:
    f.write(gitignore)

# ── Tao README.md ─────────────────────────────────────────────────────────────
readme = """# Library Management System

## Cau truc project
- `admin_app/` - Ung dung quan tri (thu thu, admin)
- `user_app/`  - Ung dung sinh vien (ban ban lam)
- `core/`      - Services, styles, config dung chung
- `database/`  - DB chung cho ca hai app
- `reports/`   - Xuat bao cao Excel

## Chay app
```bash
# Chay admin
python main.py admin

# Chay user (sinh vien)
python main.py user
```

## Tai khoan mac dinh
- Admin: username=`admin` / password=`admin123`
- Staff: username=`staff01` / password=`staff123`

## Cai dat
```bash
pip install PyQt5 pandas openpyxl
```
"""
with open(os.path.join(BASE, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme)

print("[6] Tao .gitignore va README.md xong")
print()
print("=" * 50)
print("HOAN THANH! Cau truc moi:")
print()
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git"]]
    level = root.replace(BASE, "").count(os.sep)
    indent = "  " * level
    folder = os.path.basename(root)
    if level <= 2:
        print(f"{indent}{folder}/")
        subindent = "  " * (level + 1)
        for f in files:
            if not f.endswith(".pyc"):
                print(f"{subindent}{f}")
print()
print("Chay admin: python main.py admin")
print("Chay user:  python main.py user")