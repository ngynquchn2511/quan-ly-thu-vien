import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView, QDialog,
    QTextEdit, QCheckBox, QComboBox, QTabWidget, QScrollArea,
    QSizePolicy, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
import core.styles as styles

MSG_STYLE = """
    QMessageBox { background: #F7F8FC; }
    QLabel { color: #1E293B; font-size: 14px; background: transparent; }
    QPushButton {
        background: white; color: #1E293B;
        border: 1px solid #E2E8F0; border-radius: 6px;
        padding: 8px 20px; min-width: 80px; font-size: 13px;
    }
    QPushButton:hover { background: #EBF1FD; color: #5B8DEF; border-color: #5B8DEF; }
"""

STATUS_VN = {
    "Pending":  "Chờ duyệt",
    "Approved": "Đã duyệt",
    "Rejected": "Từ chối",
    "Acquired": "Đã mua",
}
STATUS_COLOR = {
    "Pending":  (styles.WARNING_BG, "#92400E"),
    "Approved": (styles.SUCCESS_BG, "#166634"),
    "Rejected": (styles.DANGER_BG,  "#991B1B"),
    "Acquired": (styles.PRIMARY_LIGHT, styles.PRIMARY),
}


# ── Dialog thêm/sửa thông báo ────────────────────────────────────────────────
class AnnouncementDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Thêm thông báo" if not data else "Sửa thông báo")
        self.setFixedSize(560, 420)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(14)

        title_lbl = QLabel("Thêm thông báo" if not self.data else "Sửa thông báo")
        title_lbl.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:bold; font-size:16px;")
        lay.addWidget(title_lbl)
        lay.addWidget(styles.section_divider())

        lay.addWidget(styles.field_label("Tiêu đề *"))
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nhập tiêu đề thông báo...")
        self.inp_title.setStyleSheet(styles.INPUT)
        self.inp_title.setFixedHeight(42)
        lay.addWidget(self.inp_title)

        lay.addWidget(styles.field_label("Nội dung"))
        self.inp_content = QTextEdit()
        self.inp_content.setPlaceholderText("Nhập nội dung thông báo...")
        self.inp_content.setStyleSheet(styles.INPUT)
        self.inp_content.setFixedHeight(120)
        lay.addWidget(self.inp_content)

        lay.addWidget(styles.field_label("Mã sách liên quan (nếu có)"))
        self.inp_book = QLineEdit()
        self.inp_book.setPlaceholderText("VD: BK001")
        self.inp_book.setStyleSheet(styles.INPUT)
        self.inp_book.setFixedHeight(42)
        lay.addWidget(self.inp_book)

        self.chk_important = QCheckBox("Đánh dấu quan trọng")
        self.chk_important.setStyleSheet(f"color:{styles.TEXT_DARK}; border:none;")
        lay.addWidget(self.chk_important)

        if self.data:
            self.inp_title.setText(self.data.get("Title", ""))
            self.inp_content.setPlainText(self.data.get("Content", "") or "")
            self.inp_book.setText(self.data.get("RelatedBookID", "") or "")
            self.chk_important.setChecked(bool(self.data.get("IsImportant", 0)))

        lay.addStretch()
        br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc = QPushButton("Huỷ"); bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(40); bc.setMinimumWidth(90); bc.clicked.connect(self.reject)
        bs = QPushButton("Lưu"); bs.setStyleSheet(styles.BTN_PRIMARY)
        bs.setFixedHeight(40); bs.setMinimumWidth(100); bs.clicked.connect(self._save)
        br.addWidget(bc); br.addWidget(bs); lay.addLayout(br)

    def _save(self):
        if not self.inp_title.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tiêu đề."); return
        self.accept()

    def get_data(self):
        return {
            "title":           self.inp_title.text().strip(),
            "content":         self.inp_content.toPlainText().strip(),
            "related_book_id": self.inp_book.text().strip() or None,
            "is_important":    1 if self.chk_important.isChecked() else 0,
        }


# ── Dialog duyệt yêu cầu ─────────────────────────────────────────────────────
class RequestReviewDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data or {}
        self.setWindowTitle("Xử lý yêu cầu mua sách")
        self.setFixedSize(520, 380)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(12)

        t = QLabel("Xử lý yêu cầu mua sách")
        t.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:bold; font-size:16px;")
        lay.addWidget(t)
        lay.addWidget(styles.section_divider())

        info = QFrame(); info.setStyleSheet(styles.INFO_BANNER)
        il = QVBoxLayout(info); il.setContentsMargins(14, 10, 14, 10); il.setSpacing(4)
        for txt in [
            f"Sinh viên: {self.data.get('StudentName', '')} ({self.data.get('StudentID', '')})",
            f"Sách đề xuất: {self.data.get('BookTitle', '')}",
            f"Tác giả: {self.data.get('Author', '') or '—'}",
            f"Lý do: {self.data.get('Reason', '') or '—'}",
        ]:
            lbl = QLabel(txt); lbl.setStyleSheet(f"color:{styles.TEXT_DARK}; border:none;")
            il.addWidget(lbl)
        lay.addWidget(info)

        lay.addWidget(styles.field_label("Trạng thái"))
        self.cmb_status = QComboBox()
        self.cmb_status.setStyleSheet(styles.COMBO)
        self.cmb_status.setFixedHeight(40)
        self.cmb_status.addItems(["Chờ duyệt", "Đã duyệt", "Từ chối", "Đã mua"])
        cur = STATUS_VN.get(self.data.get("Status", "Pending"), "Chờ duyệt")
        self.cmb_status.setCurrentText(cur)
        lay.addWidget(self.cmb_status)

        lay.addWidget(styles.field_label("Ghi chú admin"))
        self.inp_note = QLineEdit()
        self.inp_note.setPlaceholderText("Nhập ghi chú...")
        self.inp_note.setStyleSheet(styles.INPUT)
        self.inp_note.setFixedHeight(40)
        self.inp_note.setText(self.data.get("AdminNote", "") or "")
        lay.addWidget(self.inp_note)

        lay.addWidget(styles.field_label("Mã sách đã mua (nếu Đã mua)"))
        self.inp_acquired = QLineEdit()
        self.inp_acquired.setPlaceholderText("VD: BK099")
        self.inp_acquired.setStyleSheet(styles.INPUT)
        self.inp_acquired.setFixedHeight(40)
        self.inp_acquired.setText(self.data.get("AcquiredBookID", "") or "")
        lay.addWidget(self.inp_acquired)

        lay.addStretch()
        br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc = QPushButton("Huỷ"); bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(40); bc.setMinimumWidth(90); bc.clicked.connect(self.reject)
        bs = QPushButton("Xác nhận"); bs.setStyleSheet(styles.BTN_PRIMARY)
        bs.setFixedHeight(40); bs.setMinimumWidth(100); bs.clicked.connect(self.accept)
        br.addWidget(bc); br.addWidget(bs); lay.addLayout(br)

    def get_data(self):
        STATUS_MAP = {"Chờ duyệt": "Pending", "Đã duyệt": "Approved",
                      "Từ chối":   "Rejected", "Đã mua":   "Acquired"}
        return {
            "status":          STATUS_MAP.get(self.cmb_status.currentText(), "Pending"),
            "admin_note":      self.inp_note.text().strip(),
            "acquired_book_id": self.inp_acquired.text().strip() or None,
        }


# ── Tab Thông báo ─────────────────────────────────────────────────────────────
class AnnouncementTab(QWidget):
    COLS = ["ID", "Tiêu đề", "Nội dung", "Người tạo", "Ngày tạo", "Quan trọng", "Thao tác"]

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(12)

        tb = QHBoxLayout(); tb.setSpacing(10)
        btn_add = QPushButton("+ Thêm thông báo"); btn_add.setStyleSheet(styles.BTN_PRIMARY)
        btn_add.setFixedHeight(40); btn_add.clicked.connect(self._add)
        btn_ref = QPushButton("Làm mới"); btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(40); btn_ref.clicked.connect(self.refresh)
        self.inp_search = QLineEdit(); self.inp_search.setPlaceholderText("Tìm tiêu đề, nội dung...")
        self.inp_search.setStyleSheet(styles.INPUT); self.inp_search.setFixedHeight(40)
        self.inp_search.setMinimumWidth(240); self.inp_search.textChanged.connect(self._load)
        tb.addWidget(btn_add); tb.addWidget(btn_ref); tb.addStretch(); tb.addWidget(self.inp_search)
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
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 50)
        hdr.setSectionResizeMode(1, QHeaderView.Fixed);  self.table.setColumnWidth(1, 200)
        hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed);  self.table.setColumnWidth(3, 130)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed);  self.table.setColumnWidth(4, 130)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed);  self.table.setColumnWidth(5, 120)
        hdr.setSectionResizeMode(6, QHeaderView.Fixed);  self.table.setColumnWidth(6, 140)
        lay.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color:{styles.TEXT_MUTED};")
        lay.addWidget(self.lbl_count)

    def refresh(self): self._load()

    def _load(self):
        from core.services.announcement_service import get_all_announcements
        kw   = self.inp_search.text().strip()
        rows = get_all_announcements(kw)
        self.table.setRowCount(0)
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            try: dt = datetime.strptime(r.get("CreatedAt","")[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            except: dt = r.get("CreatedAt","")
            vals = [str(r.get("AnnouncementID","")), r.get("Title",""),
                    r.get("Content","") or "", r.get("StaffName","") or "—", dt]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, col, item)

            # Badge quan trong
            is_imp = r.get("IsImportant", 0)
            bg, fg = ("#FCEBEB", "#991B1B") if is_imp else (styles.BG, styles.TEXT_MUTED)
            txt = "Quan trọng" if is_imp else "Thường"
            self.table.setCellWidget(i, 5, styles.badge_widget(txt, bg, fg, 85))

            # Nut thao tac
            ann_id = r.get("AnnouncementID")
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4, 3, 4, 3); bl.setSpacing(4)
            be = QPushButton("Sửa"); be.setStyleSheet(styles.BTN_SMALL)
            be.setFixedHeight(28); be.setFixedWidth(52)
            be.clicked.connect(lambda _, x=ann_id, d=r: self._edit(x, d))
            bd = QPushButton("Xóa"); bd.setStyleSheet(styles.BTN_SMALL_DANGER)
            bd.setFixedHeight(28); bd.setFixedWidth(52)
            bd.clicked.connect(lambda _, x=ann_id: self._delete(x))
            bl.addWidget(be); bl.addWidget(bd)
            self.table.setCellWidget(i, 6, bw)
            self.table.setRowHeight(i, 50)
        self.lbl_count.setText(f"Tổng: {len(rows)} thông báo")

    def _add(self):
        from core.services.announcement_service import add_announcement
        dlg = AnnouncementDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            staff_id = self.current_user.get("StaffID", "unknown")
            ok, msg = add_announcement(d["title"], d["content"], staff_id,
                                       d["related_book_id"], d["is_important"])
            if ok: self.refresh()

    def _edit(self, ann_id, data):
        from core.services.announcement_service import update_announcement
        dlg = AnnouncementDialog(self, data=data)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            ok, msg = update_announcement(ann_id, d["title"], d["content"],
                                          d["related_book_id"], d["is_important"])
            if ok: self.refresh()

    def _delete(self, ann_id):
        from core.services.announcement_service import delete_announcement
        msg = QMessageBox(self); msg.setWindowTitle("Xác nhận xóa")
        msg.setText("Bạn có chắc muốn xóa thông báo này?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Xóa")
        msg.button(QMessageBox.No).setText("Huỷ")
        msg.setStyleSheet(MSG_STYLE)
        if msg.exec_() == QMessageBox.Yes:
            delete_announcement(ann_id); self.refresh()


# ── Tab Yêu cầu mua sách ──────────────────────────────────────────────────────
class BookRequestTab(QWidget):
    COLS = ["ID", "Mã SV", "Họ tên", "Sách đề xuất", "Tác giả", "Ngày tạo", "Trạng thái", "Thao tác"]

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(12)

        tb = QHBoxLayout(); tb.setSpacing(10)
        btn_ref = QPushButton("Làm mới"); btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(40); btn_ref.clicked.connect(self.refresh)
        self.inp_search = QLineEdit(); self.inp_search.setPlaceholderText("Tìm tên sách, sinh viên...")
        self.inp_search.setStyleSheet(styles.INPUT); self.inp_search.setFixedHeight(40)
        self.inp_search.setMinimumWidth(220); self.inp_search.textChanged.connect(self._load)
        self.cmb_status = QComboBox(); self.cmb_status.setStyleSheet(styles.COMBO)
        self.cmb_status.setFixedHeight(40); self.cmb_status.setFixedWidth(130)
        self.cmb_status.addItems(["Tất cả", "Chờ duyệt", "Đã duyệt", "Từ chối", "Đã mua"])
        self.cmb_status.currentTextChanged.connect(self._load)
        tb.addWidget(btn_ref); tb.addStretch()
        tb.addWidget(self.inp_search); tb.addWidget(self.cmb_status)
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
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 50)
        hdr.setSectionResizeMode(1, QHeaderView.Fixed);  self.table.setColumnWidth(1, 100)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed);  self.table.setColumnWidth(2, 150)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed);  self.table.setColumnWidth(4, 130)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed);  self.table.setColumnWidth(5, 100)
        hdr.setSectionResizeMode(6, QHeaderView.Fixed);  self.table.setColumnWidth(6, 110)
        hdr.setSectionResizeMode(7, QHeaderView.Fixed);  self.table.setColumnWidth(7, 90)
        lay.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color:{styles.TEXT_MUTED};")
        lay.addWidget(self.lbl_count)

    def refresh(self): self._load()

    def _load(self):
        from core.services.announcement_service import get_book_requests
        kw     = self.inp_search.text().strip()
        status = self.cmb_status.currentText()
        rows   = get_book_requests(kw, status)
        self.table.setRowCount(0)
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            try: dt = datetime.strptime(r.get("CreatedAt","")[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            except: dt = r.get("CreatedAt","")
            vals = [str(r.get("RequestID","")), r.get("StudentID",""),
                    r.get("StudentName",""), r.get("BookTitle",""),
                    r.get("Author","") or "—", dt]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, col, item)

            st = r.get("Status", "Pending")
            bg, fg = STATUS_COLOR.get(st, (styles.BG, styles.TEXT_MUTED))
            self.table.setCellWidget(i, 6, styles.badge_widget(STATUS_VN.get(st, st), bg, fg, 90))

            req_id = r.get("RequestID")
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4, 3, 4, 3)
            btn = QPushButton("Xử lý"); btn.setStyleSheet(styles.BTN_SMALL)
            btn.setFixedHeight(28); btn.setFixedWidth(65)
            btn.clicked.connect(lambda _, x=req_id, d=r: self._review(x, d))
            bl.addWidget(btn)
            self.table.setCellWidget(i, 7, bw)
            self.table.setRowHeight(i, 50)

        pending = sum(1 for r in rows if r.get("Status") == "Pending")
        self.lbl_count.setText(f"Tổng: {len(rows)} yêu cầu  |  Chờ duyệt: {pending}")

    def _review(self, req_id, data):
        from core.services.announcement_service import update_request_status
        dlg = RequestReviewDialog(self, data=data)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            staff_id = self.current_user.get("StaffID", "unknown")
            ok, msg = update_request_status(req_id, d["status"], d["admin_note"],
                                            staff_id, d["acquired_book_id"])
            if ok: self.refresh()


# ── Tab Đánh giá sách ────────────────────────────────────────────────────────
class BookReviewTab(QWidget):
    COLS = ["ID", "Tên sách", "Sinh viên", "Đánh giá", "Nhận xét", "Ngày", "Thao tác"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(12)

        tb = QHBoxLayout(); tb.setSpacing(10)
        btn_ref = QPushButton("Làm mới"); btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(40); btn_ref.clicked.connect(self.refresh)
        self.inp_search = QLineEdit(); self.inp_search.setPlaceholderText("Tìm tên sách, sinh viên...")
        self.inp_search.setStyleSheet(styles.INPUT); self.inp_search.setFixedHeight(40)
        self.inp_search.setMinimumWidth(260); self.inp_search.textChanged.connect(self._load)
        tb.addWidget(btn_ref); tb.addStretch(); tb.addWidget(self.inp_search)
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
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 50)
        hdr.setSectionResizeMode(1, QHeaderView.Fixed);  self.table.setColumnWidth(1, 200)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed);  self.table.setColumnWidth(2, 150)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed);  self.table.setColumnWidth(3, 100)
        hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed);  self.table.setColumnWidth(5, 100)
        hdr.setSectionResizeMode(6, QHeaderView.Fixed);  self.table.setColumnWidth(6, 90)
        lay.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color:{styles.TEXT_MUTED};")
        lay.addWidget(self.lbl_count)

    def refresh(self): self._load()

    def _load(self):
        from core.services.announcement_service import get_book_reviews
        kw   = self.inp_search.text().strip()
        rows = get_book_reviews(keyword=kw)
        self.table.setRowCount(0)
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            try: dt = datetime.strptime(r.get("CreatedAt","")[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            except: dt = r.get("CreatedAt","")
            rating = r.get("Rating", 0)
            stars  = "★" * rating + "☆" * (5 - rating)
            vals = [str(r.get("ReviewID","")), r.get("BookTitle",""),
                    r.get("StudentName",""), stars,
                    r.get("Comment","") or "—", dt]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == 3:
                    item.setForeground(Qt.darkYellow)
                self.table.setItem(i, col, item)

            rev_id = r.get("ReviewID")
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4, 3, 4, 3)
            bd = QPushButton("Xóa"); bd.setStyleSheet(styles.BTN_SMALL_DANGER)
            bd.setFixedHeight(28); bd.setFixedWidth(52)
            bd.clicked.connect(lambda _, x=rev_id: self._delete(x))
            bl.addWidget(bd)
            self.table.setCellWidget(i, 6, bw)
            self.table.setRowHeight(i, 50)
        self.lbl_count.setText(f"Tổng: {len(rows)} đánh giá")

    def _delete(self, rev_id):
        from core.services.announcement_service import delete_review
        msg = QMessageBox(self); msg.setWindowTitle("Xác nhận")
        msg.setText("Xóa đánh giá này?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Xóa")
        msg.button(QMessageBox.No).setText("Huỷ")
        msg.setStyleSheet(MSG_STYLE)
        if msg.exec_() == QMessageBox.Yes:
            delete_review(rev_id); self.refresh()


# ── Tab Yêu thích theo thể loại ──────────────────────────────────────────────
class FavoritesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(12)

        tb = QHBoxLayout()
        btn_ref = QPushButton("Làm mới"); btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(40); btn_ref.clicked.connect(self.refresh)

        self.cmb_cat = QComboBox(); self.cmb_cat.setStyleSheet(styles.COMBO)
        self.cmb_cat.setFixedHeight(40); self.cmb_cat.setFixedWidth(160)
        self.cmb_cat.addItem("Tất cả thể loại")
        self.cmb_cat.currentTextChanged.connect(self._load)

        tb.addWidget(btn_ref); tb.addStretch(); tb.addWidget(self.cmb_cat)
        lay.addLayout(tb)

        # Bang
        COLS = ["Thể loại", "Tên sách", "Tác giả", "Yêu thích", "Đánh giá TB"]
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setStyleSheet(styles.TABLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 130)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed);  self.table.setColumnWidth(2, 160)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed);  self.table.setColumnWidth(3, 90)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed);  self.table.setColumnWidth(4, 100)
        lay.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color:{styles.TEXT_MUTED};")
        lay.addWidget(self.lbl_count)

    def refresh(self):
        from core.services.announcement_service import get_favorites_by_category
        rows = get_favorites_by_category()
        # Cap nhat combo the loai
        cats = sorted(set(r.get("Category","Khác") or "Khác" for r in rows))
        self.cmb_cat.blockSignals(True)
        cur = self.cmb_cat.currentText()
        self.cmb_cat.clear()
        self.cmb_cat.addItem("Tất cả thể loại")
        for c in cats: self.cmb_cat.addItem(c)
        idx = self.cmb_cat.findText(cur)
        self.cmb_cat.setCurrentIndex(max(0, idx))
        self.cmb_cat.blockSignals(False)
        self.all_rows = rows
        self._load()

    def _load(self):
        cat = self.cmb_cat.currentText()
        rows = self.all_rows if hasattr(self, 'all_rows') else []
        if cat != "Tất cả thể loại":
            rows = [r for r in rows if (r.get("Category") or "Khác") == cat]

        self.table.setRowCount(0)
        prev_cat = None
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            cat_val = r.get("Category","Khác") or "Khác"
            # Chi hien ten the loai o dong dau tien cua nhom
            cat_display = cat_val if cat_val != prev_cat else ""
            prev_cat = cat_val

            fav   = r.get("FavoriteCount", 0)
            avg_r = r.get("AvgRating")
            avg_display = f"{avg_r:.1f} ★" if avg_r else "—"

            vals = [cat_display, r.get("Title",""), r.get("Author",""),
                    str(fav), avg_display]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == 3:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.table.setItem(i, col, item)
            self.table.setRowHeight(i, 46)

        self.lbl_count.setText(f"Tổng: {len(rows)} sách được yêu thích")


# ── Window chính ──────────────────────────────────────────────────────────────
class AnnouncementWindow(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: {styles.BG}; }}
            QTabBar::tab {{
                background: {styles.WHITE}; color: {styles.TEXT_MID};
                padding: 10px 20px; border: none; font-size: 13px;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {styles.PRIMARY}; font-weight: 600;
                border-bottom: 2px solid {styles.PRIMARY};
            }}
            QTabBar::tab:hover {{ color: {styles.PRIMARY}; }}
        """)

        tabs.addTab(AnnouncementTab(self.current_user), "📢 Thông báo")
        tabs.addTab(BookRequestTab(self.current_user),  "📋 Yêu cầu mua sách")
        tabs.addTab(BookReviewTab(),                    "⭐ Đánh giá sách")
        tabs.addTab(FavoritesTab(),                     "❤ Yêu thích theo thể loại")

        lay.addWidget(tabs)

    def refresh(self):
        pass