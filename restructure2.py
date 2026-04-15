"""
Chay tu thu muc library-system:
    python restructure2.py
Chi copy phan con lai (bo qua db va file dang bi khoa)
"""
import os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))

# Chi copy database files (bo qua .db)
moves = [
    ("database/db.py",          "database/db.py"),
    ("database/models.py",      "database/models.py"),
    ("reports/export_excel.py", "reports/export_excel.py"),
]

for src, dst in moves:
    src_full = os.path.join(BASE, src)
    dst_full = os.path.join(BASE, dst)
    if src_full == dst_full:
        print(f"  [==] Da o dung cho: {src}")
        continue
    if os.path.exists(src_full):
        os.makedirs(os.path.dirname(dst_full), exist_ok=True)
        try:
            shutil.copy2(src_full, dst_full)
            print(f"  [OK] {src} -> {dst}")
        except PermissionError:
            print(f"  [!!] Bi khoa, bo qua: {src}")
    else:
        print(f"  [--] Khong ton tai: {src}")

# Tao root main.py
root_main = '''"""
ENTRY POINT CHINH
Chay admin: python main.py admin
Chay user:  python main.py user
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) < 2 or sys.argv[1] not in ["admin", "user"]:
    print("Dung: python main.py [admin|user]")
    sys.exit(1)

if sys.argv[1] == "admin":
    from admin_app.main import main
else:
    from user_app.main import main

main()
'''
with open(os.path.join(BASE, "main.py"), "w", encoding="utf-8") as f:
    f.write(root_main)
print("  [OK] main.py (root)")

# Tao admin_app/main.py
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
os.makedirs(os.path.join(BASE, "admin_app"), exist_ok=True)
with open(os.path.join(BASE, "admin_app/main.py"), "w", encoding="utf-8") as f:
    f.write(admin_main)
print("  [OK] admin_app/main.py")

# Tao __init__.py cho cac package
for pkg in ["admin_app", "admin_app/gui", "user_app", "user_app/gui",
            "core", "core/services", "core/utils", "database", "reports"]:
    init = os.path.join(BASE, pkg, "__init__.py")
    os.makedirs(os.path.dirname(init), exist_ok=True)
    if not os.path.exists(init):
        open(init, "w").close()

# Tao user_app placeholders neu chua co
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
    "user_app/gui/login_gui.py": '''import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
    "user_app/gui/home_gui.py":     "from PyQt5.QtWidgets import QWidget\nclass HomeWindow(QWidget): pass\n",
    "user_app/gui/search_gui.py":   "from PyQt5.QtWidgets import QWidget\nclass SearchWindow(QWidget): pass\n",
    "user_app/gui/my_books_gui.py": "from PyQt5.QtWidgets import QWidget\nclass MyBooksWindow(QWidget): pass\n",
    "user_app/gui/profile_gui.py":  "from PyQt5.QtWidgets import QWidget\nclass ProfileWindow(QWidget): pass\n",
}
for path, content in user_files.items():
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [NEW] {path}")

print()
print("HOAN THANH!")
print("Chay admin: python main.py admin")
print("Chay user:  python main.py user")