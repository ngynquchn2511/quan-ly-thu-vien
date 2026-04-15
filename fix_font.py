import re, os

files = [
    'gui/login_gui.py',
    'gui/dashboard.py',
    'gui/book_gui.py',
]

for fname in files:
    if not os.path.exists(fname):
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'font-size:\s*\d+px;?\s*', '', content)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done:', fname)

print('Xong! Chay python main.py')
