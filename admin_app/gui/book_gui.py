import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDialog, QMessageBox, QAbstractItemView,
    QSpinBox, QTextEdit
)
from PyQt5.QtCore import Qt
from datetime import datetime
from core.services.book_service import (
    get_all_books, add_book, update_book,
    delete_book, get_book_by_id, get_categories
)
from database.models import Book
from database.db import get_connection
import core.styles as styles


MSG_STYLE = """
    QMessageBox { background: #F7F8FC; }
    QLabel { color: #1E293B; font-size: 14px; background: transparent; }
    QPushButton {
        background: white; color: #1E293B;
        border: 1px solid #E2E8F0; border-radius: 6px;
        padding: 8px 24px; min-width: 90px; font-size: 13px;
    }
    QPushButton:hover { background: #EBF1FD; color: #5B8DEF; border-color: #5B8DEF; }
"""

# Tên hiển thị của các trường
FIELD_LABELS = {
    "Title":     "Tên sách",
    "Author":    "Tác giả",
    "Category":  "Thể loại",
    "Publisher": "Nhà xuất bản",
    "Year":      "Năm XB",
    "ISBN":      "ISBN",
    "Quantity":  "Số lượng",
    "Location":  "Vị trí kệ",
}


def build_diff(old: dict, new_book: Book) -> str:
    """So sanh sach cu va moi, tra ve chuoi mo ta thay doi."""
    new = {
        "Title":     new_book.title,
        "Author":    new_book.author,
        "Category":  new_book.category,
        "Publisher": new_book.publisher,
        "Year":      str(new_book.year),
        "ISBN":      new_book.isbn or "",
        "Quantity":  str(new_book.quantity),
        "Location":  new_book.location or "",
    }
    changes = []
    for key, label in FIELD_LABELS.items():
        old_val = str(old.get(key, "") or "")
        new_val = str(new.get(key, "") or "")
        if old_val != new_val:
            changes.append(f"{label}: «{old_val}» → «{new_val}»")
    return " | ".join(changes) if changes else "Không có thay đổi"


def write_log(staff_id, action, target_id, detail=""):
    """Ghi log vao AuditLog. detail chua mo ta chi tiet thay doi."""
    try:
        conn = get_connection(); cur = conn.cursor()
        # Kiem tra cot Detail co ton tai chua
        cur.execute("PRAGMA table_info(AuditLog)")
        cols = [r[1] for r in cur.fetchall()]
        if "Detail" not in cols:
            cur.execute("ALTER TABLE AuditLog ADD COLUMN Detail TEXT")
        cur.execute("""
            INSERT INTO AuditLog (StaffID, Action, TargetID, Timestamp, Detail)
            VALUES (?, ?, ?, ?, ?)
        """, (staff_id, action, target_id,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"), detail))
        conn.commit(); conn.close()
    except Exception as e:
        print(f"[Log] {e}")


def get_book_logs(book_id=None):
    try:
        conn = get_connection(); cur = conn.cursor()
        # Kiem tra cot Detail
        cur.execute("PRAGMA table_info(AuditLog)")
        cols = [r[1] for r in cur.fetchall()]
        has_detail = "Detail" in cols

        detail_col = "a.Detail" if has_detail else "'' as Detail"
        if book_id:
            cur.execute(f"""
                SELECT a.Timestamp, a.StaffID, s.Name, a.Action, a.TargetID, {detail_col}
                FROM AuditLog a
                LEFT JOIN Staff s ON a.StaffID = s.StaffID
                WHERE a.TargetID = ? AND a.Action IN ('Sửa sách','Xoá sách','Thêm sách')
                ORDER BY a.Timestamp DESC
            """, (book_id,))
        else:
            cur.execute(f"""
                SELECT a.Timestamp, a.StaffID, s.Name, a.Action, a.TargetID, {detail_col}
                FROM AuditLog a
                LEFT JOIN Staff s ON a.StaffID = s.StaffID
                WHERE a.Action IN ('Sửa sách','Xoá sách','Thêm sách')
                ORDER BY a.Timestamp DESC LIMIT 200
            """)
        rows = cur.fetchall(); conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_book_logs] {e}")
        return []


class HistoryDialog(QDialog):
    def __init__(self, parent=None, book_id=None, book_title=""):
        super().__init__(parent)
        title = f"Lịch sử — {book_title}" if book_id else "Lịch sử tất cả sách"
        self.setWindowTitle(title)
        self.resize(920, 520)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self.book_id = book_id
        self._build()
        self._load()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        hdr = QHBoxLayout()
        t = QLabel(self.windowTitle())
        t.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: bold; font-size: 15px;")
        btn_ref = QPushButton("Làm mới")
        btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(36)
        btn_ref.clicked.connect(self._load)
        hdr.addWidget(t); hdr.addStretch(); hdr.addWidget(btn_ref)
        lay.addLayout(hdr)
        lay.addWidget(styles.section_divider())

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Thời gian", "Mã NV", "Tên nhân viên", "Hành động", "Mã sách", "Chi tiết thay đổi"])
        self.table.setStyleSheet(styles.TABLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setWordWrap(True)

        hdr2 = self.table.horizontalHeader()
        hdr2.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 120)
        hdr2.setSectionResizeMode(1, QHeaderView.Fixed);  self.table.setColumnWidth(1, 80)
        hdr2.setSectionResizeMode(2, QHeaderView.Fixed);  self.table.setColumnWidth(2, 140)
        hdr2.setSectionResizeMode(3, QHeaderView.Fixed);  self.table.setColumnWidth(3, 130)
        hdr2.setSectionResizeMode(4, QHeaderView.Fixed);  self.table.setColumnWidth(4, 120)
        hdr2.setSectionResizeMode(5, QHeaderView.Stretch)  # Chi tiet chiem phan con lai
        lay.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color: {styles.TEXT_MUTED};")
        lay.addWidget(self.lbl_count)

        br = QHBoxLayout(); br.addStretch()
        bc = QPushButton("Đóng")
        bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(40); bc.setMinimumWidth(100)
        bc.clicked.connect(self.accept)
        br.addWidget(bc); lay.addLayout(br)

    def _load(self):
        logs = get_book_logs(self.book_id)
        self.table.setRowCount(0)

        for i, log in enumerate(logs):
            self.table.insertRow(i)
            action = log.get("Action", "")
            detail = log.get("Detail", "") or ""

            vals = [
                log.get("Timestamp", ""),
                log.get("StaffID", ""),
                log.get("Name", "") or "—",
                "",        # col 3: badge
                log.get("TargetID", ""),
                detail,
            ]
            for col, val in enumerate(vals):
                if col == 3: continue  # badge
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, col, item)

            # Badge hanh dong
            if "Xoá" in action:
                bg, fg = styles.DANGER_BG,  "#991B1B"
            elif "Sửa" in action:
                bg, fg = styles.WARNING_BG, "#92400E"
            else:
                bg, fg = styles.SUCCESS_BG, "#166634"
            self.table.setCellWidget(i, 3, styles.badge_widget(action, bg, fg, 110))

            # Chieu cao dong tu dong theo noi dung detail
            lines = max(1, len(detail) // 60 + detail.count("|") + 1)
            self.table.setRowHeight(i, max(46, lines * 22 + 14))

        self.lbl_count.setText(f"Tổng: {len(logs)} thao tác")


class BookDialog(QDialog):
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.book_data = book_data
        self.setWindowTitle("Thêm sách mới" if not book_data else "Chỉnh sửa sách")
        self.setFixedSize(640, 580)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        title = QLabel("Thêm sách mới" if not self.book_data else "Chỉnh sửa thông tin sách")
        title.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: bold; font-size: 16px;")
        lay.addWidget(title)
        lay.addWidget(styles.section_divider())

        def lbl(t): return styles.field_label(t)

        r1 = QHBoxLayout(); r1.setSpacing(16)
        c1 = QVBoxLayout(); c1.setSpacing(6)
        c1.addWidget(lbl("Mã sách *"))
        self.inp_id = QLineEdit(); self.inp_id.setPlaceholderText("BK011...")
        self.inp_id.setFixedHeight(42); self.inp_id.setStyleSheet(styles.INPUT)
        c1.addWidget(self.inp_id)
        c2 = QVBoxLayout(); c2.setSpacing(6)
        c2.addWidget(lbl("ISBN"))
        self.inp_isbn = QLineEdit(); self.inp_isbn.setPlaceholderText("978-...")
        self.inp_isbn.setFixedHeight(42); self.inp_isbn.setStyleSheet(styles.INPUT)
        c2.addWidget(self.inp_isbn)
        r1.addLayout(c1); r1.addLayout(c2); lay.addLayout(r1)

        lay.addWidget(lbl("Tên sách *"))
        self.inp_title = QLineEdit(); self.inp_title.setPlaceholderText("Nhập tên sách...")
        self.inp_title.setFixedHeight(42); self.inp_title.setStyleSheet(styles.INPUT)
        lay.addWidget(self.inp_title)

        r2 = QHBoxLayout(); r2.setSpacing(16)
        c3 = QVBoxLayout(); c3.setSpacing(6)
        c3.addWidget(lbl("Tác giả *"))
        self.inp_author = QLineEdit(); self.inp_author.setPlaceholderText("Tên tác giả...")
        self.inp_author.setFixedHeight(42); self.inp_author.setStyleSheet(styles.INPUT)
        c3.addWidget(self.inp_author)
        c4 = QVBoxLayout(); c4.setSpacing(6)
        c4.addWidget(lbl("Thể loại"))
        self.inp_cat = QComboBox(); self.inp_cat.setFixedHeight(42)
        self.inp_cat.setStyleSheet(styles.COMBO)
        self.inp_cat.addItems(["Lập trình","CNTT","Toán học","Khoa học",
                               "Ngoại ngữ","Đại cương","Kinh tế","Khác"])
        c4.addWidget(self.inp_cat)
        r2.addLayout(c3); r2.addLayout(c4); lay.addLayout(r2)

        r3 = QHBoxLayout(); r3.setSpacing(16)
        c5 = QVBoxLayout(); c5.setSpacing(6)
        c5.addWidget(lbl("Nhà xuất bản"))
        self.inp_pub = QLineEdit(); self.inp_pub.setPlaceholderText("NXB...")
        self.inp_pub.setFixedHeight(42); self.inp_pub.setStyleSheet(styles.INPUT)
        c5.addWidget(self.inp_pub)
        c6 = QVBoxLayout(); c6.setSpacing(6)
        c6.addWidget(lbl("Năm xuất bản"))
        self.inp_year = QSpinBox(); self.inp_year.setFixedHeight(42)
        self.inp_year.setRange(1900, 2100); self.inp_year.setValue(2024)
        self.inp_year.setStyleSheet(styles.INPUT)
        c6.addWidget(self.inp_year)
        r3.addLayout(c5); r3.addLayout(c6); lay.addLayout(r3)

        r4 = QHBoxLayout(); r4.setSpacing(16)
        c7 = QVBoxLayout(); c7.setSpacing(6)
        c7.addWidget(lbl("Số lượng"))
        self.inp_qty = QSpinBox(); self.inp_qty.setFixedHeight(42)
        self.inp_qty.setRange(1, 9999); self.inp_qty.setValue(1)
        self.inp_qty.setStyleSheet(styles.INPUT)
        c7.addWidget(self.inp_qty)
        c8 = QVBoxLayout(); c8.setSpacing(6)
        c8.addWidget(lbl("Vị trí kệ"))
        self.inp_loc = QLineEdit(); self.inp_loc.setPlaceholderText("A1-01")
        self.inp_loc.setFixedHeight(42); self.inp_loc.setStyleSheet(styles.INPUT)
        c8.addWidget(self.inp_loc)
        r4.addLayout(c7); r4.addLayout(c8); lay.addLayout(r4)

        if self.book_data:
            self.inp_id.setText(self.book_data.get("BookID",""))
            self.inp_id.setEnabled(False)
            self.inp_title.setText(self.book_data.get("Title",""))
            self.inp_author.setText(self.book_data.get("Author",""))
            idx = self.inp_cat.findText(self.book_data.get("Category",""))
            if idx >= 0: self.inp_cat.setCurrentIndex(idx)
            self.inp_pub.setText(self.book_data.get("Publisher","") or "")
            self.inp_year.setValue(self.book_data.get("Year",2024) or 2024)
            self.inp_isbn.setText(self.book_data.get("ISBN","") or "")
            self.inp_qty.setValue(self.book_data.get("Quantity",1))
            self.inp_loc.setText(self.book_data.get("Location","") or "")

        lay.addStretch()
        br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc = QPushButton("Huỷ"); bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(42); bc.setMinimumWidth(100); bc.clicked.connect(self.reject)
        bs = QPushButton("Lưu sách"); bs.setStyleSheet(styles.BTN_PRIMARY)
        bs.setFixedHeight(42); bs.setMinimumWidth(120); bs.clicked.connect(self._save)
        br.addWidget(bc); br.addWidget(bs); lay.addLayout(br)

    def _save(self):
        book_id = self.inp_id.text().strip()
        title   = self.inp_title.text().strip()
        author  = self.inp_author.text().strip()
        if not book_id: QMessageBox.warning(self,"Lỗi","Vui lòng nhập mã sách."); return
        if not title:   QMessageBox.warning(self,"Lỗi","Vui lòng nhập tên sách."); return
        if not author:  QMessageBox.warning(self,"Lỗi","Vui lòng nhập tác giả."); return
        qty   = self.inp_qty.value()
        avail = qty if not self.book_data else min(self.book_data.get("Available",qty), qty)
        book  = Book(
            book_id=book_id, title=title, author=author,
            category=self.inp_cat.currentText(),
            publisher=self.inp_pub.text().strip(),
            year=self.inp_year.value(),
            isbn=self.inp_isbn.text().strip(),
            quantity=qty, available=avail,
            location=self.inp_loc.text().strip()
        )
        try:
            if self.book_data: update_book(book)
            else: add_book(book)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self,"Lỗi",f"Không thể lưu: {e}")

    def get_book(self):
        """Tra ve Book object tu form."""
        qty = self.inp_qty.value()
        avail = qty if not self.book_data else min(
            self.book_data.get("Available", qty), qty)
        return Book(
            book_id=self.inp_id.text().strip(),
            title=self.inp_title.text().strip(),
            author=self.inp_author.text().strip(),
            category=self.inp_cat.currentText(),
            publisher=self.inp_pub.text().strip(),
            year=self.inp_year.value(),
            isbn=self.inp_isbn.text().strip(),
            quantity=qty, available=avail,
            location=self.inp_loc.text().strip()
        )


class BookWindow(QWidget):
    COLS = ["Mã sách","Tên sách","Tác giả","Thể loại",
            "SL","Còn","Vị trí","Trạng thái","Thao tác"]

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._build()
        self.refresh()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(14)

        tb = QHBoxLayout(); tb.setSpacing(10)
        self.btn_add = QPushButton("+ Thêm sách")
        self.btn_add.setStyleSheet(styles.BTN_PRIMARY)
        self.btn_add.setFixedHeight(40)
        self.btn_add.clicked.connect(self._add)

        self.btn_ref = QPushButton("Làm mới")
        self.btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        self.btn_ref.setFixedHeight(40)
        self.btn_ref.clicked.connect(self.refresh)

        self.btn_hist = QPushButton("📋 Lịch sử")
        self.btn_hist.setStyleSheet(styles.BTN_OUTLINE)
        self.btn_hist.setFixedHeight(40)
        self.btn_hist.clicked.connect(self._show_all_history)

        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo tên, tác giả, ISBN...")
        self.inp_search.setStyleSheet(styles.INPUT)
        self.inp_search.setFixedHeight(40)
        self.inp_search.setMinimumWidth(260)
        self.inp_search.textChanged.connect(self._load)

        self.cmb_cat = QComboBox()
        self.cmb_cat.setStyleSheet(styles.COMBO)
        self.cmb_cat.setFixedHeight(40)
        self.cmb_cat.addItem("Tất cả thể loại")
        self.cmb_cat.currentTextChanged.connect(self._load)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color: {styles.TEXT_MUTED};")

        tb.addWidget(self.btn_add); tb.addWidget(self.btn_ref); tb.addWidget(self.btn_hist)
        tb.addStretch()
        tb.addWidget(self.inp_search); tb.addWidget(self.cmb_cat)
        lay.addLayout(tb)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.setStyleSheet(styles.TABLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 110)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed);  self.table.setColumnWidth(2, 160)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed);  self.table.setColumnWidth(3, 120)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed);  self.table.setColumnWidth(4, 50)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed);  self.table.setColumnWidth(5, 50)
        hdr.setSectionResizeMode(6, QHeaderView.Fixed);  self.table.setColumnWidth(6, 90)
        hdr.setSectionResizeMode(7, QHeaderView.Fixed);  self.table.setColumnWidth(7, 110)
        hdr.setSectionResizeMode(8, QHeaderView.Fixed);  self.table.setColumnWidth(8, 180)
        lay.addWidget(self.table)
        lay.addWidget(self.lbl_count)

    def refresh(self):
        cur = self.cmb_cat.currentText()
        self.cmb_cat.blockSignals(True); self.cmb_cat.clear()
        self.cmb_cat.addItem("Tất cả thể loại")
        for c in get_categories(): self.cmb_cat.addItem(c)
        idx = self.cmb_cat.findText(cur)
        self.cmb_cat.setCurrentIndex(max(0, idx))
        self.cmb_cat.blockSignals(False)
        self._load()

    def _load(self):
        kw  = self.inp_search.text().strip()
        cat = self.cmb_cat.currentText()
        if cat == "Tất cả thể loại": cat = ""
        books = get_all_books(kw, cat)
        self.table.setRowCount(0)

        for i, b in enumerate(books):
            self.table.insertRow(i)
            qty   = b.get("Quantity", 0)
            avail = b.get("Available", 0)
            vals  = [b.get("BookID",""), b.get("Title",""), b.get("Author",""),
                     b.get("Category",""), str(qty), str(avail),
                     b.get("Location","") or ""]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(
                    Qt.AlignVCenter | (Qt.AlignCenter if col in [4,5] else Qt.AlignLeft))
                self.table.setItem(i, col, item)

            if avail == 0:   bg, fg, txt = styles.DANGER_BG,  "#991B1B", "Hết sách"
            elif avail <= 2: bg, fg, txt = styles.WARNING_BG, "#92400E", "Gần hết"
            else:            bg, fg, txt = styles.SUCCESS_BG, "#166634", "Còn sách"
            self.table.setCellWidget(i, 7, styles.badge_widget(txt, bg, fg, 90))

            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4, 3, 4, 3); bl.setSpacing(4)
            be = QPushButton("Sửa"); be.setStyleSheet(styles.BTN_SMALL)
            be.setFixedHeight(28); be.setFixedWidth(52)
            be.clicked.connect(lambda _, x=b["BookID"]: self._edit(x))
            bd = QPushButton("Xoá"); bd.setStyleSheet(styles.BTN_SMALL_DANGER)
            bd.setFixedHeight(28); bd.setFixedWidth(52)
            bd.clicked.connect(lambda _, x=b["BookID"], t=b["Title"]: self._delete(x, t))
            bh = QPushButton("Log"); bh.setStyleSheet(styles.BTN_SMALL)
            bh.setFixedHeight(28); bh.setFixedWidth(46)
            bh.clicked.connect(
                lambda _, x=b["BookID"], t=b["Title"]: self._show_history(x, t))
            bl.addWidget(be); bl.addWidget(bd); bl.addWidget(bh)
            self.table.setCellWidget(i, 8, bw)
            self.table.setRowHeight(i, 50)

        self.lbl_count.setText(f"Tổng: {len(books)} sách")

    def _add(self):
        dlg = BookDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            book_id  = dlg.inp_id.text().strip()
            staff_id = self.current_user.get("StaffID", "unknown")
            new_book = dlg.get_book()
            detail   = (f"Tên: {new_book.title} | Tác giả: {new_book.author} | "
                        f"Thể loại: {new_book.category} | SL: {new_book.quantity} | "
                        f"Vị trí: {new_book.location}")
            write_log(staff_id, "Thêm sách", book_id, detail)
            self.refresh()

    def _edit(self, book_id):
        old_data = get_book_by_id(book_id)
        if not old_data: return
        dlg = BookDialog(self, book_data=old_data)
        if dlg.exec_() == QDialog.Accepted:
            staff_id = self.current_user.get("StaffID", "unknown")
            new_book = dlg.get_book()
            detail   = build_diff(old_data, new_book)
            write_log(staff_id, "Sửa sách", book_id, detail)
            self.refresh()

    def _delete(self, book_id, book_title):
        msg = QMessageBox(self)
        msg.setWindowTitle("Xác nhận xoá")
        msg.setText(f"Bạn có chắc muốn xoá sách:\n«{book_title}»?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Xoá")
        msg.button(QMessageBox.No).setText("Huỷ")
        msg.setStyleSheet(MSG_STYLE)
        if msg.exec_() == QMessageBox.Yes:
            try:
                # Lay thong tin sach truoc khi xoa de ghi vao log
                old_data = get_book_by_id(book_id)
                detail   = ""
                if old_data:
                    detail = (f"Tên: {old_data.get('Title','')} | "
                              f"Tác giả: {old_data.get('Author','')} | "
                              f"SL: {old_data.get('Quantity','')} | "
                              f"Vị trí: {old_data.get('Location','')}")
                delete_book(book_id)
                staff_id = self.current_user.get("StaffID", "unknown")
                write_log(staff_id, "Xoá sách", book_id, detail)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _show_history(self, book_id, book_title):
        HistoryDialog(self, book_id=book_id, book_title=book_title).exec_()

    def _show_all_history(self):
        HistoryDialog(self).exec_()