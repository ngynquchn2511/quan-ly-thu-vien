import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDialog, QMessageBox, QAbstractItemView, QSpinBox
)
from PyQt5.QtCore import Qt
from core.services.book_service import (
    get_all_books, add_book, update_book,
    delete_book, get_book_by_id, get_categories
)
from database.models import Book
import core.styles as styles


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

        # Row 1: Ma sach + ISBN
        r1 = QHBoxLayout(); r1.setSpacing(16)
        c1 = QVBoxLayout(); c1.setSpacing(6)
        c1.addWidget(lbl("Mã sách *"))
        self.inp_id = QLineEdit(); self.inp_id.setFixedHeight(42)
        self.inp_id.setPlaceholderText("BK011...")
        self.inp_id.setStyleSheet(styles.INPUT)
        c1.addWidget(self.inp_id)
        c2 = QVBoxLayout(); c2.setSpacing(6)
        c2.addWidget(lbl("ISBN"))
        self.inp_isbn = QLineEdit(); self.inp_isbn.setFixedHeight(42)
        self.inp_isbn.setPlaceholderText("978-...")
        self.inp_isbn.setStyleSheet(styles.INPUT)
        c2.addWidget(self.inp_isbn)
        r1.addLayout(c1); r1.addLayout(c2)
        lay.addLayout(r1)

        # Ten sach
        lay.addWidget(lbl("Tên sách *"))
        self.inp_title = QLineEdit(); self.inp_title.setFixedHeight(42)
        self.inp_title.setPlaceholderText("Nhập tên sách...")
        self.inp_title.setStyleSheet(styles.INPUT)
        lay.addWidget(self.inp_title)

        # Row 2: Tac gia + The loai
        r2 = QHBoxLayout(); r2.setSpacing(16)
        c3 = QVBoxLayout(); c3.setSpacing(6)
        c3.addWidget(lbl("Tác giả *"))
        self.inp_author = QLineEdit(); self.inp_author.setFixedHeight(42)
        self.inp_author.setPlaceholderText("Tên tác giả...")
        self.inp_author.setStyleSheet(styles.INPUT)
        c3.addWidget(self.inp_author)
        c4 = QVBoxLayout(); c4.setSpacing(6)
        c4.addWidget(lbl("Thể loại"))
        self.inp_cat = QComboBox(); self.inp_cat.setFixedHeight(42)
        self.inp_cat.setStyleSheet(styles.COMBO)
        self.inp_cat.addItems(["Lập trình", "CNTT", "Toán học", "Khoa học",
                               "Ngoại ngữ", "Đại cương", "Kinh tế", "Khác"])
        c4.addWidget(self.inp_cat)
        r2.addLayout(c3); r2.addLayout(c4)
        lay.addLayout(r2)

        # Row 3: NXB + Nam
        r3 = QHBoxLayout(); r3.setSpacing(16)
        c5 = QVBoxLayout(); c5.setSpacing(6)
        c5.addWidget(lbl("Nhà xuất bản"))
        self.inp_pub = QLineEdit(); self.inp_pub.setFixedHeight(42)
        self.inp_pub.setPlaceholderText("NXB...")
        self.inp_pub.setStyleSheet(styles.INPUT)
        c5.addWidget(self.inp_pub)
        c6 = QVBoxLayout(); c6.setSpacing(6)
        c6.addWidget(lbl("Năm xuất bản"))
        self.inp_year = QSpinBox(); self.inp_year.setFixedHeight(42)
        self.inp_year.setRange(1900, 2100); self.inp_year.setValue(2024)
        self.inp_year.setStyleSheet(styles.INPUT)
        c6.addWidget(self.inp_year)
        r3.addLayout(c5); r3.addLayout(c6)
        lay.addLayout(r3)

        # Row 4: So luong + Vi tri
        r4 = QHBoxLayout(); r4.setSpacing(16)
        c7 = QVBoxLayout(); c7.setSpacing(6)
        c7.addWidget(lbl("Số lượng"))
        self.inp_qty = QSpinBox(); self.inp_qty.setFixedHeight(42)
        self.inp_qty.setRange(1, 9999); self.inp_qty.setValue(1)
        self.inp_qty.setStyleSheet(styles.INPUT)
        c7.addWidget(self.inp_qty)
        c8 = QVBoxLayout(); c8.setSpacing(6)
        c8.addWidget(lbl("Vị trí kệ"))
        self.inp_loc = QLineEdit(); self.inp_loc.setFixedHeight(42)
        self.inp_loc.setPlaceholderText("A1-01")
        self.inp_loc.setStyleSheet(styles.INPUT)
        c8.addWidget(self.inp_loc)
        r4.addLayout(c7); r4.addLayout(c8)
        lay.addLayout(r4)

        # Dien san du lieu neu la sua
        if self.book_data:
            self.inp_id.setText(self.book_data.get("BookID", ""))
            self.inp_id.setEnabled(False)
            self.inp_title.setText(self.book_data.get("Title", ""))
            self.inp_author.setText(self.book_data.get("Author", ""))
            idx = self.inp_cat.findText(self.book_data.get("Category", ""))
            if idx >= 0: self.inp_cat.setCurrentIndex(idx)
            self.inp_pub.setText(self.book_data.get("Publisher", "") or "")
            self.inp_year.setValue(self.book_data.get("Year", 2024) or 2024)
            self.inp_isbn.setText(self.book_data.get("ISBN", "") or "")
            self.inp_qty.setValue(self.book_data.get("Quantity", 1))
            self.inp_loc.setText(self.book_data.get("Location", "") or "")

        lay.addStretch()

        # Buttons
        br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc = QPushButton("Huỷ"); bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(42); bc.setMinimumWidth(100)
        bc.clicked.connect(self.reject)
        bs = QPushButton("Lưu sách"); bs.setStyleSheet(styles.BTN_PRIMARY)
        bs.setFixedHeight(42); bs.setMinimumWidth(120)
        bs.clicked.connect(self._save)
        br.addWidget(bc); br.addWidget(bs)
        lay.addLayout(br)

    def _save(self):
        book_id = self.inp_id.text().strip()
        title   = self.inp_title.text().strip()
        author  = self.inp_author.text().strip()
        if not book_id: QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã sách."); return
        if not title:   QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên sách."); return
        if not author:  QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tác giả."); return
        qty   = self.inp_qty.value()
        avail = qty if not self.book_data else min(self.book_data.get("Available", qty), qty)
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
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")


class BookWindow(QWidget):
    COLS = ["Mã sách", "Tên sách", "Tác giả", "Thể loại",
            "SL", "Còn", "Vị trí", "Trạng thái", "Thao tác"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self.refresh()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(14)

        # Toolbar
        tb = QHBoxLayout(); tb.setSpacing(10)
        self.btn_add = QPushButton("+ Thêm sách")
        self.btn_add.setStyleSheet(styles.BTN_PRIMARY)
        self.btn_add.setFixedHeight(40)
        self.btn_add.clicked.connect(self._add)

        self.btn_ref = QPushButton("Làm mới")
        self.btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        self.btn_ref.setFixedHeight(40)
        self.btn_ref.clicked.connect(self.refresh)

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

        tb.addWidget(self.btn_add); tb.addWidget(self.btn_ref)
        tb.addStretch()
        tb.addWidget(self.inp_search); tb.addWidget(self.cmb_cat)
        lay.addLayout(tb)

        # Table
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
        hdr.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 110)   # Ma sach
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Ten sach
        hdr.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 160)   # Tac gia
        hdr.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 120)   # The loai
        hdr.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 55)    # SL
        hdr.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 55)    # Con
        hdr.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 90)    # Vi tri
        hdr.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 120)   # Trang thai
        hdr.setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 140)   # Thao tac

        lay.addWidget(self.table)
        lay.addWidget(self.lbl_count)

    def refresh(self):
        cur = self.cmb_cat.currentText()
        self.cmb_cat.blockSignals(True)
        self.cmb_cat.clear()
        self.cmb_cat.addItem("Tất cả thể loại")
        for c in get_categories():
            self.cmb_cat.addItem(c)
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

            vals = [
                b.get("BookID", ""),
                b.get("Title", ""),
                b.get("Author", ""),
                b.get("Category", ""),
                str(qty),
                str(avail),
                b.get("Location", "") or ""
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(
                    Qt.AlignVCenter | (Qt.AlignCenter if col in [4, 5] else Qt.AlignLeft)
                )
                self.table.setItem(i, col, item)

            # Badge trang thai
            if avail == 0:
                bg, fg, txt = styles.DANGER_BG,  "#991B1B", "Hết sách"
            elif avail <= 2:
                bg, fg, txt = styles.WARNING_BG, "#92400E", "Gần hết"
            else:
                bg, fg, txt = styles.SUCCESS_BG, "#166534", "Còn sách"
            self.table.setCellWidget(i, 7, styles.badge_widget(txt, bg, fg, 90))

            # Nut thao tac
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(6, 4, 6, 4); bl.setSpacing(8)
            be = QPushButton("Sửa")
            be.setStyleSheet(styles.BTN_SMALL)
            be.setFixedHeight(30); be.setFixedWidth(60)
            be.clicked.connect(lambda _, x=b["BookID"]: self._edit(x))
            bd = QPushButton("Xoá")
            bd.setStyleSheet(styles.BTN_SMALL_DANGER)
            bd.setFixedHeight(30); bd.setFixedWidth(60)
            bd.clicked.connect(lambda _, x=b["BookID"]: self._delete(x))
            bl.addWidget(be); bl.addWidget(bd)
            self.table.setCellWidget(i, 8, bw)
            self.table.setRowHeight(i, 50)

        self.lbl_count.setText(f"Tổng: {len(books)} sách")

    def _add(self):
        if BookDialog(self).exec_() == QDialog.Accepted:
            self.refresh()

    def _edit(self, book_id):
        data = get_book_by_id(book_id)
        if data and BookDialog(self, book_data=data).exec_() == QDialog.Accepted:
            self.refresh()

    def _delete(self, book_id):
        if QMessageBox.question(
            self, "Xác nhận xoá",
            f"Bạn có chắc muốn xoá sách '{book_id}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                delete_book(book_id)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))