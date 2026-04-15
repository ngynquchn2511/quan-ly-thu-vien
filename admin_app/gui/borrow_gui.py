import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from services.borrow_service import borrow_book, return_book, get_active_borrows, update_overdue_status
from services.student_service import get_student_by_id
from services.book_service import get_book_by_id
from datetime import datetime, timedelta
import styles


class InfoChip(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {styles.BG};
                border: 1px solid {styles.BORDER};
                border-radius: 8px;
            }}
        """)
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(12, 10, 12, 10)
        self._lay.setSpacing(12)
        self.setFixedHeight(56)
        self.hide()

    def set_content(self, initials, title, subtitle, ok=True):
        while self._lay.count():
            item = self._lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        av = QLabel(initials[:2].upper())
        av.setFixedSize(34, 34)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(
            f"background: {styles.PRIMARY}; color: white;"
            f"border-radius: 17px; font-weight: bold; border: none;"
        )
        self._lay.addWidget(av)

        info = QVBoxLayout(); info.setSpacing(1)
        t = QLabel(title)
        t.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: 600; border: none;")
        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 12px; border: none;")
        info.addWidget(t); info.addWidget(s)
        self._lay.addLayout(info)
        self._lay.addStretch()

        bg, fg = (styles.SUCCESS_BG, "#166534") if ok else (styles.DANGER_BG, "#991B1B")
        badge_text = "Hợp lệ" if ok else "Không hợp lệ"
        self._lay.addWidget(styles.make_badge(badge_text, bg, fg, 90))
        self.show()


class BorrowWindow(QWidget):
    COLS = ["Mã phiếu", "Mã SV", "Họ tên", "Tên sách",
            "Ngày mượn", "Hạn trả", "Trạng thái", "Thao tác"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self.refresh_table()

    def _build(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── CỘT TRÁI: Form mượn ──────────────────────────────────────────────
        left = QFrame()
        left.setStyleSheet(f"""
            QFrame {{
                background: {styles.WHITE};
                border-right: 1px solid {styles.BORDER};
            }}
        """)
        left.setFixedWidth(380)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(20, 18, 20, 18)
        ll.setSpacing(12)

        title = QLabel("Phiếu mượn sách mới")
        title.setStyleSheet(
            f"color: {styles.TEXT_DARK}; font-weight: bold; font-size: 15px; border: none;"
        )
        ll.addWidget(title)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {styles.BORDER}; max-height: 1px; border: none;")
        ll.addWidget(div)

        def lbl(t): return styles.field_label(t)

        # Ma SV
        ll.addWidget(lbl("Mã sinh viên"))
        sv_row = QHBoxLayout(); sv_row.setSpacing(8)
        self.inp_sv = QLineEdit()
        self.inp_sv.setPlaceholderText("Nhập mã SV...")
        self.inp_sv.setStyleSheet(styles.INPUT)
        self.inp_sv.setFixedHeight(40)
        btn_sv = QPushButton("Tìm")
        btn_sv.setStyleSheet(styles.BTN_PRIMARY)
        btn_sv.setFixedSize(70, 40)
        btn_sv.clicked.connect(self._lookup_sv)
        sv_row.addWidget(self.inp_sv); sv_row.addWidget(btn_sv)
        ll.addLayout(sv_row)

        self.chip_sv = InfoChip()
        ll.addWidget(self.chip_sv)

        # Ma sach
        ll.addWidget(lbl("Mã sách / ISBN"))
        bk_row = QHBoxLayout(); bk_row.setSpacing(8)
        self.inp_bk = QLineEdit()
        self.inp_bk.setPlaceholderText("Nhập mã sách...")
        self.inp_bk.setStyleSheet(styles.INPUT)
        self.inp_bk.setFixedHeight(40)
        btn_bk = QPushButton("Tìm")
        btn_bk.setStyleSheet(styles.BTN_PRIMARY)
        btn_bk.setFixedSize(70, 40)
        btn_bk.clicked.connect(self._lookup_bk)
        bk_row.addWidget(self.inp_bk); bk_row.addWidget(btn_bk)
        ll.addLayout(bk_row)

        self.chip_bk = InfoChip()
        ll.addWidget(self.chip_bk)

        # Ngay muon / han tra
        date_row = QHBoxLayout(); date_row.setSpacing(12)
        dl = QVBoxLayout(); dl.setSpacing(4)
        dl.addWidget(lbl("Ngày mượn"))
        self.lbl_bd = QLabel(datetime.now().strftime("%d/%m/%Y"))
        self.lbl_bd.setStyleSheet(
            f"color: {styles.TEXT_DARK}; background: {styles.BG};"
            f"border: 1px solid {styles.BORDER}; border-radius: 8px; padding: 10px 13px;"
        )
        self.lbl_bd.setFixedHeight(42)
        dl.addWidget(self.lbl_bd)

        dr = QVBoxLayout(); dr.setSpacing(4)
        dr.addWidget(lbl("Hạn trả (14 ngày)"))
        self.lbl_dd = QLabel((datetime.now() + timedelta(days=14)).strftime("%d/%m/%Y"))
        self.lbl_dd.setStyleSheet(
            f"color: {styles.TEXT_DARK}; background: {styles.BG};"
            f"border: 1px solid {styles.BORDER}; border-radius: 8px; padding: 10px 13px;"
        )
        self.lbl_dd.setFixedHeight(42)
        dr.addWidget(self.lbl_dd)

        date_row.addLayout(dl); date_row.addLayout(dr)
        ll.addLayout(date_row)
        ll.addStretch()

        self.btn_borrow = QPushButton("Xác nhận mượn sách")
        self.btn_borrow.setStyleSheet(styles.BTN_PRIMARY)
        self.btn_borrow.setFixedHeight(46)
        self.btn_borrow.clicked.connect(self._do_borrow)
        ll.addWidget(self.btn_borrow)
        main.addWidget(left)

        # ── CỘT PHẢI: Danh sách đang mượn ────────────────────────────────────
        right_w = QWidget()
        right_w.setStyleSheet(f"background: {styles.BG};")
        rl = QVBoxLayout(right_w)
        rl.setContentsMargins(16, 18, 16, 18)
        rl.setSpacing(12)

        sr = QHBoxLayout(); sr.setSpacing(8)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo mã SV, tên sách...")
        self.inp_search.setStyleSheet(styles.INPUT)
        self.inp_search.setFixedHeight(40)
        self.inp_search.textChanged.connect(self.refresh_table)
        btn_ref = QPushButton("Làm mới")
        btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(40)
        btn_ref.clicked.connect(self.refresh_table)
        sr.addWidget(self.inp_search); sr.addWidget(btn_ref)
        rl.addLayout(sr)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color: {styles.TEXT_MUTED};")
        rl.addWidget(self.lbl_count)

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
        self.table.setColumnWidth(0, 90)    # Ma phieu
        hdr.setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 110)   # Ma SV
        hdr.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 160)   # Ho ten
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)  # Ten sach
        hdr.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 110)   # Ngay muon
        hdr.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 100)   # Han tra
        hdr.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 110)   # Trang thai
        hdr.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 110)   # Thao tac

        rl.addWidget(self.table)
        main.addWidget(right_w)

    def _lookup_sv(self):
        sid = self.inp_sv.text().strip()
        if not sid: return
        data = get_student_by_id(sid)
        if not data:
            QMessageBox.warning(self, "Không tìm thấy", "Không tìm thấy sinh viên.")
            return
        exp   = data.get("CardExpire", "") or ""
        valid = exp >= datetime.now().strftime("%Y-%m-%d") if exp else False
        try:
            exp_disp = datetime.strptime(exp, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            exp_disp = exp
        self.chip_sv.set_content(
            data.get("Name", "")[:2],
            data.get("Name", ""),
            f"{data.get('Class','')} — {data.get('Faculty','')} | Hạn thẻ: {exp_disp}",
            valid
        )

    def _lookup_bk(self):
        bid = self.inp_bk.text().strip()
        if not bid: return
        data = get_book_by_id(bid)
        if not data:
            QMessageBox.warning(self, "Không tìm thấy", "Không tìm thấy sách.")
            return
        avail = data.get("Available", 0)
        self.chip_bk.set_content(
            data.get("Title", "")[:2],
            data.get("Title", ""),
            f"Tác giả: {data.get('Author','')} | Còn lại: {avail} cuốn | Kệ: {data.get('Location','')}",
            avail > 0
        )

    def _do_borrow(self):
        sid = self.inp_sv.text().strip()
        bid = self.inp_bk.text().strip()
        if not sid or not bid:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập mã SV và mã sách.")
            return
        ok, msg = borrow_book(sid, bid)
        if ok:
            QMessageBox.information(self, "Thành công", msg)
            self.inp_sv.clear(); self.inp_bk.clear()
            self.chip_sv.hide(); self.chip_bk.hide()
            self.refresh_table()
        else:
            QMessageBox.warning(self, "Không thể mượn", msg)

    def refresh_table(self):
        update_overdue_status()
        kw   = self.inp_search.text().strip() if hasattr(self, "inp_search") else ""
        rows = get_active_borrows(kw)
        self.table.setRowCount(0)
        today = datetime.now().strftime("%Y-%m-%d")

        for i, r in enumerate(rows):
            self.table.insertRow(i)
            due    = r.get("DueDate", "")
            status = r.get("Status", "")

            try:
                bd = datetime.strptime(r.get("BorrowDate",""), "%Y-%m-%d").strftime("%d/%m/%Y")
                dd = datetime.strptime(due, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                bd = r.get("BorrowDate", ""); dd = due

            vals = [
                str(r.get("BorrowID", "")),
                r.get("StudentID", ""),
                r.get("StudentName", ""),
                r.get("BookTitle", ""),
                bd, dd
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, col, item)

            # Badge trang thai
            if status == "Overdue":
                bg, fg, txt = styles.DANGER_BG,  "#991B1B", "Quá hạn"
            elif due < today:
                bg, fg, txt = styles.WARNING_BG, "#92400E", "Sắp hạn"
            else:
                bg, fg, txt = styles.SUCCESS_BG, "#166634", "Đúng hạn"
            self.table.setCellWidget(i, 6, styles.badge_widget(txt, bg, fg, 90))

            # Nut tra sach
            bid_val = r.get("BorrowID")
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(6, 4, 6, 4)
            btn_ret = QPushButton("Trả sách")
            btn_ret.setStyleSheet(styles.BTN_SMALL)
            btn_ret.setFixedHeight(30)
            btn_ret.clicked.connect(lambda _, b=bid_val: self._do_return(b))
            bl.addWidget(btn_ret)
            self.table.setCellWidget(i, 7, bw)
            self.table.setRowHeight(i, 48)

        self.lbl_count.setText(f"Đang mượn: {len(rows)} lượt")

    def _do_return(self, borrow_id):
        if QMessageBox.question(
            self, "Xác nhận trả",
            "Xác nhận trả sách này?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.Yes:
            ok, msg, fine = return_book(borrow_id)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Lỗi", msg)