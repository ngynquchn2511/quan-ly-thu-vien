"""
Chay tu thu muc library-system:
    python fix_cols.py
Tang width cot Sua/Xoa va cot Thao tac
"""
import os

fixes = {
    "gui/book_gui.py": [
        ("self.table.setColumnWidth(7, 110)", "self.table.setColumnWidth(7, 120)"),
        ("self.table.setColumnWidth(8, 120)", "self.table.setColumnWidth(8, 140)"),
    ],
    "gui/student_gui.py": [
        ("self.table.setColumnWidth(7, 110)", "self.table.setColumnWidth(7, 120)"),
        ("self.table.setColumnWidth(8, 120)", "self.table.setColumnWidth(8, 140)"),
    ],
    "gui/staff_gui.py": [
        ("self.table.setColumnWidth(3, 120)", "self.table.setColumnWidth(3, 130)"),
        ("self.table.setColumnWidth(4, 130)", "self.table.setColumnWidth(4, 140)"),
        ("self.table.setColumnWidth(5, 100)", "self.table.setColumnWidth(5, 120)"),
    ],
    "gui/borrow_gui.py": [
        ("self.table.setColumnWidth(6, 110)", "self.table.setColumnWidth(6, 120)"),
        ("self.table.setColumnWidth(7, 100)", "self.table.setColumnWidth(7, 120)"),
    ],
}

for fname, replacements in fixes.items():
    if not os.path.exists(fname):
        print(f"Skip: {fname}"); continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] {fname}")

print("Xong! Chay python main.py")