import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView, QDialog,
    QDoubleSpinBox, QScrollArea
)
from PyQt5.QtCore import Qt
from core.services.borrow_service import (
    borrow_book, return_book, get_active_borrows,
    update_overdue_status, mark_lost, resolve_lost
)
from core.services.student_service import get_student_by_id
from core.services.book_service import get_book_by_id
from database.db import get_connection
from datetime import datetime, timedelta
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


def get_borrow_history(keyword=""):
    """Lay lich su tat ca phieu muon (ca da tra)."""
    try:
        conn = get_connection(); cur = conn.cursor()
        kw = f"%{keyword}%"
        cur.execute("""
            SELECT b.BorrowID, b.StudentID, s.Name as StudentName,
                   bk.Title as BookTitle, b.BorrowDate, b.DueDate,
                   b.ReturnDate, b.Status, b.FineAmount, b.FinePaid, b.LostDate
            FROM Borrow b
            JOIN Students s  ON b.StudentID=s.StudentID
            JOIN Books bk    ON b.BookID=bk.BookID
            WHERE (b.StudentID LIKE ? OR s.Name LIKE ? OR bk.Title LIKE ?)
            ORDER BY b.BorrowID DESC
            LIMIT 200
        """, (kw, kw, kw))
        rows = cur.fetchall(); conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[history] {e}"); return []


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lịch sử mượn trả sách")
        self.resize(1100, 580)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self._build(); self._load()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(20,18,20,18); lay.setSpacing(12)

        hdr = QHBoxLayout()
        t = QLabel("Lịch sử mượn trả sách")
        t.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:bold; font-size:15px;")
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo mã SV, tên sách...")
        self.inp_search.setStyleSheet(styles.INPUT); self.inp_search.setFixedHeight(36)
        self.inp_search.setMinimumWidth(240)
        self.inp_search.textChanged.connect(self._load)
        btn_ref = QPushButton("Làm mới"); btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(36); btn_ref.clicked.connect(self._load)
        hdr.addWidget(t); hdr.addStretch()
        hdr.addWidget(self.inp_search); hdr.addWidget(btn_ref)
        lay.addLayout(hdr)
        lay.addWidget(styles.section_divider())

        COLS = ["Mã phiếu","Mã SV","Họ tên","Tên sách",
                "Ngày mượn","Hạn trả","Ngày trả","Trạng thái","Tiền phạt","Đã nộp"]
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

        hdr2 = self.table.horizontalHeader()
        hdr2.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 80)
        hdr2.setSectionResizeMode(1, QHeaderView.Fixed);  self.table.setColumnWidth(1, 110)
        hdr2.setSectionResizeMode(2, QHeaderView.Fixed);  self.table.setColumnWidth(2, 160)
        hdr2.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr2.setSectionResizeMode(4, QHeaderView.Fixed);  self.table.setColumnWidth(4, 105)
        hdr2.setSectionResizeMode(5, QHeaderView.Fixed);  self.table.setColumnWidth(5, 100)
        hdr2.setSectionResizeMode(6, QHeaderView.Fixed);  self.table.setColumnWidth(6, 100)
        hdr2.setSectionResizeMode(7, QHeaderView.Fixed);  self.table.setColumnWidth(7, 110)
        hdr2.setSectionResizeMode(8, QHeaderView.Fixed);  self.table.setColumnWidth(8, 95)
        hdr2.setSectionResizeMode(9, QHeaderView.Fixed);  self.table.setColumnWidth(9, 80)
        lay.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color:{styles.TEXT_MUTED};")
        lay.addWidget(self.lbl_count)

        br = QHBoxLayout(); br.addStretch()
        bc = QPushButton("Đóng"); bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(40); bc.setMinimumWidth(100); bc.clicked.connect(self.accept)
        br.addWidget(bc); lay.addLayout(br)

    def _load(self):
        kw   = self.inp_search.text().strip()
        rows = get_borrow_history(kw)
        self.table.setRowCount(0)

        for i, r in enumerate(rows):
            self.table.insertRow(i)
            status = r.get("Status","")
            fine   = r.get("FineAmount",0) or 0
            paid   = r.get("FinePaid",0)

            try: bd = datetime.strptime(r.get("BorrowDate",""),"%Y-%m-%d").strftime("%d/%m/%Y")
            except: bd = r.get("BorrowDate","")
            try: dd = datetime.strptime(r.get("DueDate",""),"%Y-%m-%d").strftime("%d/%m/%Y")
            except: dd = r.get("DueDate","")
            try: rd = datetime.strptime(r.get("ReturnDate",""),"%Y-%m-%d").strftime("%d/%m/%Y")
            except: rd = "—"

            vals = [str(r.get("BorrowID","")), r.get("StudentID",""),
                    r.get("StudentName",""), r.get("BookTitle",""),
                    bd, dd, rd, "", f"{fine:,.0f}đ" if fine>0 else "—",
                    "Đã nộp" if paid else ("Còn nợ" if fine>0 else "—")]
            for col, val in enumerate(vals):
                if col == 7: continue
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, col, item)

            # Badge trang thai
            if status == "Lost":        bg,fg,txt = styles.DANGER_BG,"#991B1B","Mất sách"
            elif status == "Overdue":   bg,fg,txt = styles.WARNING_BG,"#92400E","Quá hạn"
            elif status == "Returned":  bg,fg,txt = styles.SUCCESS_BG,"#166634","Đã trả"
            else:                       bg,fg,txt = styles.PRIMARY_LIGHT,styles.PRIMARY,"Đang mượn"
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4,4,4,4)
            bl.addWidget(styles.make_badge(txt, bg, fg, 90))
            self.table.setCellWidget(i, 7, bw)
            self.table.setRowHeight(i, 46)

        self.lbl_count.setText(f"Tổng: {len(rows)} phiếu")


class LostBookDialog(QDialog):
    def __init__(self, parent, borrow_id, student_name, book_title, book_price=0):
        super().__init__(parent)
        self.borrow_id = borrow_id
        self.setWindowTitle("Xử lý mất sách")
        self.setFixedSize(480, 320)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self._build(student_name, book_title, book_price)

    def _build(self, student_name, book_title, book_price):
        lay = QVBoxLayout(self); lay.setContentsMargins(28,24,28,24); lay.setSpacing(14)
        title = QLabel("Xử lý sách bị mất")
        title.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:bold; font-size:16px;")
        lay.addWidget(title); lay.addWidget(styles.section_divider())
        info = QFrame(); info.setStyleSheet(styles.INFO_BANNER)
        il = QVBoxLayout(info); il.setContentsMargins(14,10,14,10); il.setSpacing(4)
        for text in [f"Sinh viên: {student_name}", f"Sách: {book_title}"]:
            lbl = QLabel(text); lbl.setStyleSheet(f"color:{styles.TEXT_DARK}; border:none;")
            il.addWidget(lbl)
        lay.addWidget(info)
        warn = QLabel("⚠ Thẻ sinh viên sẽ bị KHÓA sau khi xác nhận mất sách!")
        warn.setStyleSheet(f"color:{styles.DANGER}; font-weight:600; border:none;")
        warn.setWordWrap(True); lay.addWidget(warn)
        fl = QHBoxLayout(); fl.setSpacing(10)
        fl.addWidget(styles.field_label("Tiền phạt (đ):"))
        self.inp_fine = QDoubleSpinBox()
        self.inp_fine.setRange(0, 99_999_999); self.inp_fine.setSingleStep(10000)
        self.inp_fine.setDecimals(0)
        self.inp_fine.setValue(book_price * 1.5 if book_price > 0 else 200000)
        self.inp_fine.setStyleSheet(styles.INPUT); self.inp_fine.setFixedHeight(42)
        fl.addWidget(self.inp_fine); lay.addLayout(fl)
        lay.addStretch()
        br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc = QPushButton("Huỷ"); bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(40); bc.setMinimumWidth(90); bc.clicked.connect(self.reject)
        bs = QPushButton("Xác nhận mất sách"); bs.setStyleSheet("""
            QPushButton { background:#EF4444; color:white; border:none;
                border-radius:8px; padding:9px 20px; font-weight:600; }
            QPushButton:hover { background:#DC2626; }
        """)
        bs.setFixedHeight(40); bs.clicked.connect(self.accept)
        br.addWidget(bc); br.addWidget(bs); lay.addLayout(br)

    def get_fine(self): return self.inp_fine.value()


class InfoChip(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background:{styles.BG}; border:1px solid {styles.BORDER}; border-radius:8px; }}")
        self._lay = QHBoxLayout(self); self._lay.setContentsMargins(12,10,12,10); self._lay.setSpacing(12)
        self.setFixedHeight(56); self.hide()

    def set_content(self, initials, title, subtitle, ok=True):
        while self._lay.count():
            item = self._lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        av = QLabel(initials[:2].upper()); av.setFixedSize(34,34); av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"background:{styles.PRIMARY}; color:white; border-radius:17px; font-weight:bold; border:none;")
        self._lay.addWidget(av)
        info = QVBoxLayout(); info.setSpacing(1)
        t = QLabel(title); t.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:600; border:none;")
        s = QLabel(subtitle); s.setStyleSheet(f"color:{styles.TEXT_MUTED}; font-size:12px; border:none;")
        info.addWidget(t); info.addWidget(s)
        self._lay.addLayout(info); self._lay.addStretch()
        bg, fg = (styles.SUCCESS_BG,"#166634") if ok else (styles.DANGER_BG,"#991B1B")
        self._lay.addWidget(styles.make_badge("Hợp lệ" if ok else "Không hợp lệ", bg, fg, 90))
        self.show()


class BorrowWindow(QWidget):
    COLS = ["Mã phiếu","Mã SV","Họ tên","Tên sách",
            "Ngày mượn","Hạn trả","Trạng thái","Tiền phạt","Thao tác"]

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._build()
        self.refresh_table()

    def _build(self):
        main = QHBoxLayout(self); main.setContentsMargins(0,0,0,0); main.setSpacing(0)

        # LEFT
        left = QFrame()
        left.setStyleSheet(f"QFrame {{ background:{styles.WHITE}; border-right:1px solid {styles.BORDER}; }}")
        left.setFixedWidth(380)
        ll = QVBoxLayout(left); ll.setContentsMargins(20,18,20,18); ll.setSpacing(12)
        title = QLabel("Phiếu mượn sách mới")
        title.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:bold; font-size:15px; border:none;")
        ll.addWidget(title)
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background:{styles.BORDER}; max-height:1px; border:none;")
        ll.addWidget(div)

        def lbl(t): return styles.field_label(t)

        ll.addWidget(lbl("Mã sinh viên"))
        sv_row = QHBoxLayout(); sv_row.setSpacing(8)
        self.inp_sv = QLineEdit(); self.inp_sv.setPlaceholderText("Nhập mã SV...")
        self.inp_sv.setStyleSheet(styles.INPUT); self.inp_sv.setFixedHeight(40)
        btn_sv = QPushButton("Tìm"); btn_sv.setStyleSheet(styles.BTN_PRIMARY)
        btn_sv.setFixedSize(70,40); btn_sv.clicked.connect(self._lookup_sv)
        sv_row.addWidget(self.inp_sv); sv_row.addWidget(btn_sv)
        ll.addLayout(sv_row)
        self.chip_sv = InfoChip(); ll.addWidget(self.chip_sv)

        ll.addWidget(lbl("Mã sách / ISBN"))
        bk_row = QHBoxLayout(); bk_row.setSpacing(8)
        self.inp_bk = QLineEdit(); self.inp_bk.setPlaceholderText("Nhập mã sách...")
        self.inp_bk.setStyleSheet(styles.INPUT); self.inp_bk.setFixedHeight(40)
        btn_bk = QPushButton("Tìm"); btn_bk.setStyleSheet(styles.BTN_PRIMARY)
        btn_bk.setFixedSize(70,40); btn_bk.clicked.connect(self._lookup_bk)
        bk_row.addWidget(self.inp_bk); bk_row.addWidget(btn_bk)
        ll.addLayout(bk_row)
        self.chip_bk = InfoChip(); ll.addWidget(self.chip_bk)

        date_row = QHBoxLayout(); date_row.setSpacing(12)
        dl = QVBoxLayout(); dl.setSpacing(4); dl.addWidget(lbl("Ngày mượn"))
        self.lbl_bd = QLabel(datetime.now().strftime("%d/%m/%Y"))
        self.lbl_bd.setStyleSheet(f"color:{styles.TEXT_DARK}; background:{styles.BG}; border:1px solid {styles.BORDER}; border-radius:8px; padding:10px 13px;")
        self.lbl_bd.setFixedHeight(42); dl.addWidget(self.lbl_bd)
        dr = QVBoxLayout(); dr.setSpacing(4); dr.addWidget(lbl("Hạn trả (14 ngày)"))
        self.lbl_dd = QLabel((datetime.now()+timedelta(days=14)).strftime("%d/%m/%Y"))
        self.lbl_dd.setStyleSheet(f"color:{styles.TEXT_DARK}; background:{styles.BG}; border:1px solid {styles.BORDER}; border-radius:8px; padding:10px 13px;")
        self.lbl_dd.setFixedHeight(42); dr.addWidget(self.lbl_dd)
        date_row.addLayout(dl); date_row.addLayout(dr); ll.addLayout(date_row)
        ll.addStretch()
        self.btn_borrow = QPushButton("Xác nhận mượn sách")
        self.btn_borrow.setStyleSheet(styles.BTN_PRIMARY)
        self.btn_borrow.setFixedHeight(46); self.btn_borrow.clicked.connect(self._do_borrow)
        ll.addWidget(self.btn_borrow)
        main.addWidget(left)

        # RIGHT
        right_w = QWidget(); right_w.setStyleSheet(f"background:{styles.BG};")
        rl = QVBoxLayout(right_w); rl.setContentsMargins(16,18,16,18); rl.setSpacing(12)

        sr = QHBoxLayout(); sr.setSpacing(8)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo mã SV, tên sách...")
        self.inp_search.setStyleSheet(styles.INPUT); self.inp_search.setFixedHeight(40)
        self.inp_search.textChanged.connect(self.refresh_table)
        btn_ref = QPushButton("Làm mới"); btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedHeight(40); btn_ref.clicked.connect(self.refresh_table)
        btn_hist = QPushButton("📋 Lịch sử"); btn_hist.setStyleSheet(styles.BTN_OUTLINE)
        btn_hist.setFixedHeight(40); btn_hist.clicked.connect(self._show_history)
        sr.addWidget(self.inp_search); sr.addWidget(btn_ref); sr.addWidget(btn_hist)
        rl.addLayout(sr)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color:{styles.TEXT_MUTED};")
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
        hdr.setSectionResizeMode(0, QHeaderView.Fixed); self.table.setColumnWidth(0, 80)   # Ma phieu
        hdr.setSectionResizeMode(1, QHeaderView.Fixed); self.table.setColumnWidth(1, 120)  # Ma SV
        hdr.setSectionResizeMode(2, QHeaderView.Fixed); self.table.setColumnWidth(2, 160)  # Ho ten
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)                                   # Ten sach
        hdr.setSectionResizeMode(4, QHeaderView.Fixed); self.table.setColumnWidth(4, 110)  # Ngay muon
        hdr.setSectionResizeMode(5, QHeaderView.Fixed); self.table.setColumnWidth(5, 105)  # Han tra
        hdr.setSectionResizeMode(6, QHeaderView.Fixed); self.table.setColumnWidth(6, 120)  # Trang thai
        hdr.setSectionResizeMode(7, QHeaderView.Fixed); self.table.setColumnWidth(7, 100)  # Tien phat
        hdr.setSectionResizeMode(8, QHeaderView.Fixed); self.table.setColumnWidth(8, 140)  # Thao tac
        rl.addWidget(self.table)
        main.addWidget(right_w)

    def _lookup_sv(self):
        sid = self.inp_sv.text().strip()
        if not sid: return
        data = get_student_by_id(sid)
        if not data:
            QMessageBox.warning(self,"Không tìm thấy","Không tìm thấy sinh viên."); return
        exp = data.get("CardExpire","") or ""
        valid = exp >= datetime.now().strftime("%Y-%m-%d") if exp else False
        blocked = data.get("CardStatus","") == "blocked"
        if blocked: valid = False
        try: exp_disp = datetime.strptime(exp,"%Y-%m-%d").strftime("%d/%m/%Y")
        except: exp_disp = exp
        status_text = "Bị khóa" if blocked else f"Hạn thẻ: {exp_disp}"
        self.chip_sv.set_content(data.get("Name","")[:2], data.get("Name",""),
            f"{data.get('Class','')} — {data.get('Faculty','')} | {status_text}", valid)

    def _lookup_bk(self):
        bid = self.inp_bk.text().strip()
        if not bid: return
        data = get_book_by_id(bid)
        if not data:
            QMessageBox.warning(self,"Không tìm thấy","Không tìm thấy sách."); return
        avail = data.get("Available",0)
        self.chip_bk.set_content(data.get("Title","")[:2], data.get("Title",""),
            f"Tác giả: {data.get('Author','')} | Còn: {avail} cuốn | Kệ: {data.get('Location','')}",
            avail > 0)

    def _do_borrow(self):
        sid = self.inp_sv.text().strip(); bid = self.inp_bk.text().strip()
        if not sid or not bid:
            QMessageBox.warning(self,"Thiếu thông tin","Vui lòng nhập mã SV và mã sách."); return
        ok, msg = borrow_book(sid, bid)
        if ok:
            QMessageBox.information(self,"Thành công",msg)
            self.inp_sv.clear(); self.inp_bk.clear()
            self.chip_sv.hide(); self.chip_bk.hide()
            self.refresh_table()
        else:
            QMessageBox.warning(self,"Không thể mượn",msg)

    def refresh_table(self):
        update_overdue_status()
        kw   = self.inp_search.text().strip() if hasattr(self,"inp_search") else ""
        rows = get_active_borrows(kw)
        self.table.setRowCount(0)
        today = datetime.now().strftime("%Y-%m-%d")

        for i, r in enumerate(rows):
            self.table.insertRow(i)
            due    = r.get("DueDate","")
            status = r.get("Status","")
            fine   = r.get("FineAmount",0) or 0

            try: bd = datetime.strptime(r.get("BorrowDate",""),"%Y-%m-%d").strftime("%d/%m/%Y")
            except: bd = r.get("BorrowDate","")
            try: dd = datetime.strptime(due,"%Y-%m-%d").strftime("%d/%m/%Y")
            except: dd = due

            vals = [str(r.get("BorrowID","")), r.get("StudentID",""),
                    r.get("StudentName",""), r.get("BookTitle",""), bd, dd]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, col, item)

            # Badge trang thai (khong co button)
            if status == "Lost":
                bg, fg, txt = styles.DANGER_BG, "#991B1B", "Mất sách"
            elif status == "Overdue":
                try: days_over = (datetime.strptime(today,"%Y-%m-%d") - datetime.strptime(due,"%Y-%m-%d")).days
                except: days_over = 0
                if days_over > 30: bg, fg, txt = "#450A0A", "#FCA5A5", "Nguy hiểm!"
                else:              bg, fg, txt = styles.DANGER_BG, "#991B1B", "Quá hạn"
            else:
                bg, fg, txt = styles.SUCCESS_BG, "#166634", "Đúng hạn"

            bw_badge = QWidget(); bl_badge = QHBoxLayout(bw_badge)
            bl_badge.setContentsMargins(6,4,6,4)
            bl_badge.addWidget(styles.make_badge(txt, bg, fg, 100))
            self.table.setCellWidget(i, 6, bw_badge)

            # Tien phat
            fine_lbl = QLabel(f"{fine:,.0f}đ" if fine > 0 else "—")
            fine_lbl.setAlignment(Qt.AlignCenter)
            fine_lbl.setStyleSheet(
                f"color:{styles.DANGER if fine>0 else styles.TEXT_MUTED}; "
                f"font-weight:{'600' if fine>0 else '400'}; border:none; background: transparent;")
            self.table.setCellWidget(i, 7, fine_lbl)

            # Nut thao tac
            bid_val  = r.get("BorrowID")
            book_id  = r.get("BookID","")
            sv_name  = r.get("StudentName","")
            bk_title = r.get("BookTitle","")
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4,3,4,3); bl.setSpacing(4)

            if status != "Lost":
                btn_ret = QPushButton("Trả"); btn_ret.setStyleSheet(styles.BTN_SMALL)
                btn_ret.setFixedHeight(28); btn_ret.setFixedWidth(48)
                btn_ret.clicked.connect(lambda _, b=bid_val: self._do_return(b))
                btn_lost = QPushButton("Mất"); btn_lost.setStyleSheet(styles.BTN_SMALL_DANGER)
                btn_lost.setFixedHeight(28); btn_lost.setFixedWidth(48)
                btn_lost.clicked.connect(
                    lambda _, b=bid_val, bk=book_id, sn=sv_name, bt=bk_title:
                    self._do_lost(b, bk, sn, bt))
                bl.addWidget(btn_ret); bl.addWidget(btn_lost)
            else:
                btn_res = QPushButton("Xử lý"); btn_res.setStyleSheet(styles.BTN_SMALL)
                btn_res.setFixedHeight(28); btn_res.setFixedWidth(65)
                btn_res.clicked.connect(lambda _, b=bid_val: self._do_resolve(b))
                bl.addWidget(btn_res)

            self.table.setCellWidget(i, 8, bw)
            self.table.setRowHeight(i, 50)

        count_lost    = sum(1 for r in rows if r.get("Status")=="Lost")
        count_overdue = sum(1 for r in rows if r.get("Status")=="Overdue")
        self.lbl_count.setText(
            f"Đang mượn: {len(rows)} lượt  |  Quá hạn: {count_overdue}  |  Mất sách: {count_lost}")

    def _do_return(self, borrow_id):
        msg = QMessageBox(self); msg.setWindowTitle("Xác nhận trả")
        msg.setText("Xác nhận trả sách này?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Xác nhận")
        msg.button(QMessageBox.No).setText("Huỷ")
        msg.setStyleSheet(MSG_STYLE)
        if msg.exec_() == QMessageBox.Yes:
            ok, msg_text, fine = return_book(borrow_id)
            if ok: QMessageBox.information(self,"Thành công",msg_text); self.refresh_table()
            else:  QMessageBox.warning(self,"Lỗi",msg_text)

    def _do_lost(self, borrow_id, book_id, sv_name, bk_title):
        data = get_book_by_id(book_id)
        price = data.get("Price",0) if data else 0
        dlg = LostBookDialog(self, borrow_id, sv_name, bk_title, price)
        if dlg.exec_() == QDialog.Accepted:
            fine = dlg.get_fine()
            staff_id = self.current_user.get("StaffID","unknown")
            ok, msg = mark_lost(borrow_id, fine, staff_id)
            if ok: QMessageBox.information(self,"Đã xử lý",msg); self.refresh_table()
            else:  QMessageBox.warning(self,"Lỗi",msg)

    def _do_resolve(self, borrow_id):
        msg = QMessageBox(self); msg.setWindowTitle("Xác nhận giải quyết")
        msg.setText("Xác nhận sinh viên đã nộp phạt?\nThẻ sinh viên sẽ được mở khóa.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Xác nhận"); msg.button(QMessageBox.No).setText("Huỷ")
        msg.setStyleSheet(MSG_STYLE)
        if msg.exec_() == QMessageBox.Yes:
            staff_id = self.current_user.get("StaffID","unknown")
            ok, msg_text = resolve_lost(borrow_id, staff_id)
            if ok: QMessageBox.information(self,"Thành công",msg_text); self.refresh_table()
            else:  QMessageBox.warning(self,"Lỗi",msg_text)

    def _show_history(self):
        HistoryDialog(self).exec_()