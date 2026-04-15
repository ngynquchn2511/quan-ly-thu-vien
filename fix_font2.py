import re, os

files = [
    'gui/login_gui.py',
    'gui/dashboard.py',
    'gui/book_gui.py',
    'gui/student_gui.py',
    'gui/borrow_gui.py',
    'gui/staff_gui.py',
    'gui/reports_gui.py',
]

for fname in files:
    if not os.path.exists(fname):
        print(f"Skip: {fname}")
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    before = content
    content = re.sub(r'font-size:\s*[\d.]+px;?\s*', '', content)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    count = before.count('font-size')
    print(f"[OK] {fname} — da xoa {count} font-size")

print("\nXong! Chay python main.py")