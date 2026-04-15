import re, os

fixes = {
    "gui/book_gui.py": [
        ('hdr.setSectionResizeMode(7, QHeaderView.ResizeToContents)',
         'hdr.setSectionResizeMode(7, QHeaderView.Fixed)\n        self.table.setColumnWidth(7, 90)'),
        ('hdr.setSectionResizeMode(8, QHeaderView.ResizeToContents)',
         'hdr.setSectionResizeMode(8, QHeaderView.Fixed)\n        self.table.setColumnWidth(8, 110)'),
    ],
    "gui/student_gui.py": [
        ('hdr.setSectionResizeMode(7, QHeaderView.ResizeToContents)',
         'hdr.setSectionResizeMode(7, QHeaderView.Fixed)\n        self.table.setColumnWidth(7, 90)'),
        ('hdr.setSectionResizeMode(8, QHeaderView.ResizeToContents)',
         'hdr.setSectionResizeMode(8, QHeaderView.Fixed)\n        self.table.setColumnWidth(8, 110)'),
    ],
    "gui/borrow_gui.py": [
        ('hdr.setSectionResizeMode(6, QHeaderView.ResizeToContents)',
         'hdr.setSectionResizeMode(6, QHeaderView.Fixed)\n            self.table.setColumnWidth(6, 90)'),
        ('hdr.setSectionResizeMode(7, QHeaderView.ResizeToContents)',
         'hdr.setSectionResizeMode(7, QHeaderView.Fixed)\n            self.table.setColumnWidth(7, 90)'),
    ],
}

for fname, replacements in fixes.items():
    if not os.path.exists(fname):
        print(f"Skip: {fname}")
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] {fname}")

print("Xong! Chay python main.py")