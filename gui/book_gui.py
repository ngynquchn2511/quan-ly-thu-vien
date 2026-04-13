# Quan ly sach
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDialog, QFormLayout,
    QSpinBox, QMessageBox, QAbstractItemView, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

from services.book_service import (
    get_all_books, add_book, update_book,
    delete_book, get_book_by_id, get_categories
)
from database.models import Book
from config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_BG,
    COLOR_WHITE, COLOR_TEXT_DARK, COLOR_TEXT_MID,
    COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_DANGER
)

# ── Styles ─────────────────────────────────────────────────────────────────────
STYLE_TOOLBAR_BTN = f"""
    QPushButton {{
        background: {COLOR_PRIMARY};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 7px 16px;
        font-size: 16px;
        font-weight: bold;
        font-family: 'Times New Roman';
    }}
    QPushButton:hover   {{ background: {COLOR_PRIMARY_DARK}; }}
    QPushButton:pressed {{ background: #5A7BC4; }}
"""
STYLE_OUTLINE_BTN = f"""
    QPushButton {{
        background: {COLOR_WHITE};
        color: {COLOR_TEXT_MID};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 7px 16px;
        font-size: 16px;
        font-family: 'Times New Roman';
    }}
    QPushButton:hover {{ background: {COLOR_PRIMARY_BG}; color: {COLOR_PRIMARY}; }}
"""
STYLE_SEARCH = f"""
    QLineEdit {{
        background: {COLOR_WHITE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 16px;
        font-family: 'Times New Roman';
        color: {COLOR_TEXT_DARK};
    }}
    QLineEdit:focus {{ border: 1px solid {COLOR_PRIMARY}; }}
"""
STYLE_COMBO = f"""
    QComboBox {{
        background: {COLOR_WHITE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 16px;
        font-family: 'Times New Roman';
        color: {COLOR_TEXT_MID};
        min-width: 140px;
    }}
    QComboBox:focus {{ border: 1px solid {COLOR_PRIMARY}; }}
    QComboBox::drop-down {{ border: none; width: 20px; }}
"""
STYLE_TABLE = f"""
    QTableWidget {{
        background: {COLOR_WHITE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        gridline-color: {COLOR_BORDER};
        font-size: 16px;
        font-family: 'Times New Roman';
        color: {COLOR_TEXT_DARK};
    }}
    QTableWidget::item {{ padding: 6px 10px; border: none; }}
    QTableWidget::item:selected {{
        background: {COLOR_PRIMARY_BG};
        color: {COLOR_PRIMARY_DARK};
    }}
    QHeaderView::section {{
        background: {COLOR_PRIMARY_BG};
        color: {COLOR_PRIMARY_DARK};
        font-weight: bold;
        font-size: 16px;
        font-family: 'Times New Roman';
        padding: 8px 10px;
        border: none;
        border-bottom: 1px solid {COLOR_BORDER};
        border-right: 1px solid {COLOR_BORDER};
    }}
"""
STYLE_ACTION_BTN = """
    QPushButton {
        border-radius: 4px;
        border: 1px solid #DDE6F8;
        background: white;
        font-size: 16px;
        padding: 3px 8px;
        font-family: 'Times New Roman';
    }
"""
STYLE_DIALOG_INPUT = f"""
    QLineEdit, QSpinBox, QComboBox {{
        background: {COLOR_PRIMARY_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 7px 10px;
        font-size: 15px;
        font-family: 'Times New Roman';
        color: {COLOR_TEXT_DARK};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {COLOR_PRIMARY};
        background: {COLOR_WHITE};
    }}
"""


# ── Badge trạng thái ───────────────────────────────────────────────────────────
def make_badge(text, bg, fg):
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"background: {bg}; color: {fg}; border-radius: 8px;"
        f"padding: 2px 10px; font-size: 16px; font-weight: bold;"
        f"font-family: 'Times New Roman';"
    )
    lbl.setFixedHeight(22)
    return lbl


# ── Dialog Thêm / Sửa sách ────────────────────────────────────────────────────
class BookDialog(QDialog):
    def __init__(self, parent=None, book_data: dict = None):
        super().__init__(parent)
        self.book_data = book_data
        self.setWindowTitle("Thêm sách" if not book_data else "Sửa sách")
        self.setFixedSize(480, 520)
        self.setStyleSheet(f"background: {COLOR_WHITE};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        # Tiêu đề
        title = QLabel("Thêm sách mới" if not self.book_data else "Chỉnh sửa sách")
        title.setFont(QFont("Times New Roman", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        lay.addWidget(title)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {COLOR_BORDER};")
        lay.addWidget(div)

        # Form
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def field_label(text):
            l = QLabel(text)
            l.setStyleSheet(
                f"color: {COLOR_TEXT_MID}; font-size: 16px;"
                "font-family: 'Times New Roman';"
            )
            return l

        self.inp_id        = QLineEdit()
        self.inp_title     = QLineEdit()
        self.inp_author    = QLineEdit()
        self.inp_category  = QComboBox()
        self.inp_publisher = QLineEdit()
        self.inp_year      = QSpinBox()
        self.inp_isbn      = QLineEdit()
        self.inp_quantity  = QSpinBox()
        self.inp_location  = QLineEdit()

        self.inp_year.setRange(1900, 2100)
        self.inp_year.setValue(2024)
        self.inp_quantity.setRange(1, 9999)
        self.inp_quantity.setValue(1)

        cats = ["Lập trình", "CNTT", "Toán học", "Khoa học",
                "Ngoại ngữ", "Đại cương", "Kinh tế", "Khác"]
        self.inp_category.addItems(cats)

        for w in [self.inp_id, self.inp_title, self.inp_author,
                  self.inp_publisher, self.inp_isbn, self.inp_location]:
            w.setStyleSheet(STYLE_DIALOG_INPUT)
            w.setFixedHeight(36)
        for w in [self.inp_year, self.inp_quantity]:
            w.setStyleSheet(STYLE_DIALOG_INPUT)
            w.setFixedHeight(36)
        self.inp_category.setStyleSheet(STYLE_DIALOG_INPUT)
        self.inp_category.setFixedHeight(36)

        # Layout 2 cột
        row1 = QHBoxLayout()
        c1   = QVBoxLayout()
        c1.addWidget(field_label("Mã sách *"))
        c1.addWidget(self.inp_id)
        c2   = QVBoxLayout()
        c2.addWidget(field_label("ISBN"))
        c2.addWidget(self.inp_isbn)
        row1.addLayout(c1)
        row1.addSpacing(10)
        row1.addLayout(c2)
        lay.addLayout(row1)

        lay.addWidget(field_label("Tên sách *"))
        lay.addWidget(self.inp_title)

        row2 = QHBoxLayout()
        c3   = QVBoxLayout()
        c3.addWidget(field_label("Tác giả *"))
        c3.addWidget(self.inp_author)
        c4   = QVBoxLayout()
        c4.addWidget(field_label("Thể loại"))
        c4.addWidget(self.inp_category)
        row2.addLayout(c3)
        row2.addSpacing(10)
        row2.addLayout(c4)
        lay.addLayout(row2)

        row3 = QHBoxLayout()
        c5   = QVBoxLayout()
        c5.addWidget(field_label("Nhà xuất bản"))
        c5.addWidget(self.inp_publisher)
        c6   = QVBoxLayout()
        c6.addWidget(field_label("Năm XB"))
        c6.addWidget(self.inp_year)
        row3.addLayout(c5)
        row3.addSpacing(10)
        row3.addLayout(c6)
        lay.addLayout(row3)

        row4 = QHBoxLayout()
        c7   = QVBoxLayout()
        c7.addWidget(field_label("Số lượng"))
        c7.addWidget(self.inp_quantity)
        c8   = QVBoxLayout()
        c8.addWidget(field_label("Vị trí kệ"))
        c8.addWidget(self.inp_location)
        row4.addLayout(c7)
        row4.addSpacing(10)
        row4.addLayout(c8)
        lay.addLayout(row4)

        # Nếu sửa thì điền sẵn dữ liệu
        if self.book_data:
            self.inp_id.setText(self.book_data.get("BookID", ""))
            self.inp_id.setEnabled(False)
            self.inp_title.setText(self.book_data.get("Title", ""))
            self.inp_author.setText(self.book_data.get("Author", ""))
            cat = self.book_data.get("Category", "")
            idx = self.inp_category.findText(cat)
            if idx >= 0:
                self.inp_category.setCurrentIndex(idx)
            self.inp_publisher.setText(self.book_data.get("Publisher", "") or "")
            self.inp_year.setValue(self.book_data.get("Year", 2024) or 2024)
            self.inp_isbn.setText(self.book_data.get("ISBN", "") or "")
            self.inp_quantity.setValue(self.book_data.get("Quantity", 1))
            self.inp_location.setText(self.book_data.get("Location", "") or "")

        lay.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Huỷ")
        btn_cancel.setStyleSheet(STYLE_OUTLINE_BTN)
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Lưu sách")
        btn_save.setStyleSheet(STYLE_TOOLBAR_BTN)
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(8)
        btn_row.addWidget(btn_save)
        lay.addLayout(btn_row)

    def _save(self):
        book_id = self.inp_id.text().strip()
        title   = self.inp_title.text().strip()
        author  = self.inp_author.text().strip()

        if not book_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã sách.")
            return
        if not title:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên sách.")
            return
        if not author:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tác giả.")
            return

        qty = self.inp_quantity.value()
        avail = qty if not self.book_data else min(
            self.book_data.get("Available", qty), qty
        )

        book = Book(
            book_id   = book_id,
            title     = title,
            author    = author,
            category  = self.inp_category.currentText(),
            publisher = self.inp_publisher.text().strip(),
            year      = self.inp_year.value(),
            isbn      = self.inp_isbn.text().strip(),
            quantity  = qty,
            available = avail,
            location  = self.inp_location.text().strip(),
        )
        try:
            if self.book_data:
                update_book(book)
            else:
                add_book(book)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")

    def get_book(self):
        return self.inp_id.text().strip()


# ── Màn hình Quản lý Sách ──────────────────────────────────────────────────────
class BookWindow(QWidget):
    COLS = ["Mã sách", "Tên sách", "Tác giả", "Thể loại",
            "SL", "Còn", "Vị trí", "Trạng thái", ""]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self.refresh()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_add = QPushButton("+ Thêm sách")
        self.btn_add.setStyleSheet(STYLE_TOOLBAR_BTN)
        self.btn_add.setFixedHeight(36)
        self.btn_add.clicked.connect(self._add)

        self.btn_refresh = QPushButton("Làm mới")
        self.btn_refresh.setStyleSheet(STYLE_OUTLINE_BTN)
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.clicked.connect(self.refresh)

        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo tên, tác giả, ISBN...")
        self.inp_search.setStyleSheet(STYLE_SEARCH)
        self.inp_search.setFixedHeight(36)
        self.inp_search.setMinimumWidth(220)
        self.inp_search.textChanged.connect(self._on_search)

        self.cmb_cat = QComboBox()
        self.cmb_cat.setStyleSheet(STYLE_COMBO)
        self.cmb_cat.setFixedHeight(36)
        self.cmb_cat.addItem("Tất cả thể loại")
        self.cmb_cat.currentTextChanged.connect(self._on_search)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 16px; font-family: 'Times New Roman';")

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        toolbar.addWidget(self.inp_search)
        toolbar.addWidget(self.cmb_cat)
        lay.addLayout(toolbar)

        # ── Bảng dữ liệu ─────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.setStyleSheet(STYLE_TABLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setFocusPolicy(Qt.NoFocus)

        # Độ rộng cột
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(8, QHeaderView.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(STYLE_TABLE + """
            QTableWidget { alternate-background-color: #F8FAFF; }
        """)

        lay.addWidget(self.table)

        # Đếm kết quả
        lay.addWidget(self.lbl_count)

    # ── Load dữ liệu ──────────────────────────────────────────────────────────
    def refresh(self):
        self._reload_categories()
        self._load_data()

    def _reload_categories(self):
        current = self.cmb_cat.currentText()
        self.cmb_cat.blockSignals(True)
        self.cmb_cat.clear()
        self.cmb_cat.addItem("Tất cả thể loại")
        for cat in get_categories():
            self.cmb_cat.addItem(cat)
        idx = self.cmb_cat.findText(current)
        self.cmb_cat.setCurrentIndex(max(0, idx))
        self.cmb_cat.blockSignals(False)

    def _load_data(self):
        keyword = self.inp_search.text().strip()
        cat = self.cmb_cat.currentText()
        if cat == "Tất cả thể loại":
            cat = ""
        books = get_all_books(keyword, cat)
        self._fill_table(books)

    def _fill_table(self, books):
        self.table.setRowCount(0)
        for row_idx, b in enumerate(books):
            self.table.insertRow(row_idx)
            qty   = b.get("Quantity", 0)
            avail = b.get("Available", 0)

            vals = [
                b.get("BookID", ""),
                b.get("Title", ""),
                b.get("Author", ""),
                b.get("Category", ""),
                str(qty),
                str(avail),
                b.get("Location", "") or "",
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col in [4, 5]:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col, item)

            # Badge trạng thái
            if avail == 0:
                badge = make_badge("Hết sách", "#FFF5F5", COLOR_DANGER)
            elif avail <= 2:
                badge = make_badge("Gần hết", "#FFFAF0", COLOR_WARNING)
            else:
                badge = make_badge("Còn sách", "#F0FFF4", "#276749")
            cell_w = QWidget()
            cell_l = QHBoxLayout(cell_w)
            cell_l.setContentsMargins(6, 2, 6, 2)
            cell_l.addWidget(badge)
            self.table.setCellWidget(row_idx, 7, cell_w)

            # Nút sửa / xoá
            btn_w   = QWidget()
            btn_lay = QHBoxLayout(btn_w)
            btn_lay.setContentsMargins(4, 2, 4, 2)
            btn_lay.setSpacing(4)

            btn_edit = QPushButton("Sửa")
            btn_edit.setStyleSheet(STYLE_ACTION_BTN +
                f"color: {COLOR_PRIMARY}; border-color: {COLOR_PRIMARY_BG};")
            btn_edit.setFixedSize(48, 26)
            btn_edit.clicked.connect(lambda _, bid=b["BookID"]: self._edit(bid))

            btn_del = QPushButton("Xoá")
            btn_del.setStyleSheet(STYLE_ACTION_BTN +
                f"color: {COLOR_DANGER}; border-color: #FEB2B2;")
            btn_del.setFixedSize(48, 26)
            btn_del.clicked.connect(lambda _, bid=b["BookID"]: self._delete(bid))

            btn_lay.addWidget(btn_edit)
            btn_lay.addWidget(btn_del)
            self.table.setCellWidget(row_idx, 8, btn_w)

        self.table.setRowHeight
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 40)

        self.lbl_count.setText(f"Tổng: {len(books)} sách")

    def _on_search(self):
        self._load_data()

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def _add(self):
        dlg = BookDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()

    def _edit(self, book_id: str):
        data = get_book_by_id(book_id)
        if not data:
            return
        dlg = BookDialog(self, book_data=data)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()

    def _delete(self, book_id: str):
        reply = QMessageBox.question(
            self, "Xác nhận xoá",
            f"Bạn có chắc muốn xoá sách '{book_id}' không?\nHành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                delete_book(book_id)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xoá: {e}")