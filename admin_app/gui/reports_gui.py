import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database.db import get_connection
import styles


class ReportCard(QFrame):
    def __init__(self, icon, title, desc, callback, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(110)
        self._normal_style = f"""
            QFrame {{
                background: {styles.WHITE};
                border: 1px solid {styles.BORDER};
                border-radius: 12px;
            }}
        """
        self._hover_style = f"""
            QFrame {{
                background: {styles.PRIMARY_LIGHT};
                border: 2px solid {styles.PRIMARY};
                border-radius: 12px;
            }}
        """
        self.setStyleSheet(self._normal_style)
        lay = QVBoxLayout(self); lay.setContentsMargins(18,14,18,14); lay.setSpacing(8)
        top = QHBoxLayout()
        ic = QLabel(icon); ic.setFixedSize(38,38); ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"background: {styles.PRIMARY_LIGHT}; border-radius: 10px; border: none; font-size: 18px;")
        top.addWidget(ic); top.addStretch(); lay.addLayout(top)
        t = QLabel(title); t.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: 600; border: none;")
        d = QLabel(desc);  d.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
        lay.addWidget(t); lay.addWidget(d)

    def mousePressEvent(self, e):
        if self.callback: self.callback()

    def enterEvent(self, e): self.setStyleSheet(self._hover_style)
    def leaveEvent(self, e):  self.setStyleSheet(self._normal_style)


class ReportsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build(); self._load_stats()

    def _build(self):
        scroll = QScrollArea(self); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame); scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        lay = QVBoxLayout(container); lay.setContentsMargins(24,18,24,18); lay.setSpacing(16)

        # Grid cards
        grid = QGridLayout(); grid.setSpacing(12)
        cards = [
            ("📄","Bao cao muon tra",    "Xuat Excel theo ky",      self._export_borrow),
            ("📊","Thong ke sach",       "Top sach muon nhieu",     self._show_top_books),
            ("⚠", "Danh sach qua han",  "Kem tien phat",           self._show_overdue),
            ("👤","Thong ke doc gia",    "Hoat dong theo thang",    self._show_students),
            ("💰","Bao cao tien phat",   "Tien phat thu duoc",      self._show_fines),
            ("📑","Xuat Excel tat ca",   "Toan bo du lieu",         self._export_borrow),
        ]
        for idx,(icon,title,desc,cb) in enumerate(cards):
            grid.addWidget(ReportCard(icon,title,desc,cb), idx//3, idx%3)
        lay.addLayout(grid)

        # Bieu do the loai
        panel = QFrame(); panel.setStyleSheet(styles.CARD)
        pl = QVBoxLayout(panel); pl.setContentsMargins(20,16,20,16); pl.setSpacing(12)
        ph = QLabel("Thong ke muon sach theo the loai")
        ph.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: 600; border: none;")
        pl.addWidget(ph)
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {styles.BORDER}; max-height: 1px; border: none;")
        pl.addWidget(div)
        self.bar_container = QVBoxLayout(); self.bar_container.setSpacing(10)
        pl.addLayout(self.bar_container)
        lay.addWidget(panel)

        # Bang ket qua
        self.result_label = QLabel()
        self.result_label.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: 600; border: none;")
        self.result_label.hide()
        lay.addWidget(self.result_label)

        self.table = QTableWidget()
        self.table.setStyleSheet(styles.TABLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.hide()
        lay.addWidget(self.table)
        lay.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

    def _load_stats(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT bk.Category, COUNT(*) as cnt FROM Borrow b
                JOIN Books bk ON b.BookID=bk.BookID
                GROUP BY bk.Category ORDER BY cnt DESC LIMIT 6
            """)
            rows = cur.fetchall(); conn.close()
        except: rows = []

        while self.bar_container.count():
            item = self.bar_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not rows:
            lbl = QLabel("Chua co du lieu."); lbl.setStyleSheet(f"color: {styles.TEXT_MUTED}; border: none;")
            self.bar_container.addWidget(lbl); return

        max_cnt = max(r[1] for r in rows) or 1
        for cat, cnt in rows:
            row_w = QWidget()
            row_l = QHBoxLayout(row_w); row_l.setContentsMargins(0,0,0,0); row_l.setSpacing(12)
            lbl_cat = QLabel(cat or "Khac")
            lbl_cat.setFixedWidth(110); lbl_cat.setStyleSheet(f"color: {styles.TEXT_MID}; border: none;")
            track = QFrame(); track.setFixedHeight(10)
            track.setStyleSheet(f"background: {styles.BG}; border-radius: 5px; border: 1px solid {styles.BORDER};")
            pct = int(cnt/max_cnt*100)
            fill = QFrame(track); fill.setFixedHeight(10)
            fill.setStyleSheet(f"background: {styles.PRIMARY}; border-radius: 5px; border: none;")
            fill.setFixedWidth(max(8, int(pct*2.8)))
            lbl_cnt = QLabel(f"{cnt} luot")
            lbl_cnt.setStyleSheet(f"color: {styles.TEXT_MID}; border: none;"); lbl_cnt.setFixedWidth(65)
            row_l.addWidget(lbl_cat); row_l.addWidget(track,1); row_l.addWidget(lbl_cnt)
            self.bar_container.addWidget(row_w)

    def _show_table(self, title, headers, rows):
        self.result_label.setText(title); self.result_label.show()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(0)
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
                self.table.setItem(i,j,item)
            self.table.setRowHeight(i,44)
        hdr = self.table.horizontalHeader()
        for c in range(len(headers)): hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        if headers: hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.show()

    def _show_top_books(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT bk.Title, bk.Author, COUNT(*) as cnt FROM Borrow b
            JOIN Books bk ON b.BookID=bk.BookID GROUP BY b.BookID ORDER BY cnt DESC LIMIT 10
        """)
        rows = cur.fetchall(); conn.close()
        self._show_table("Top 10 sach muon nhieu nhat",["Ten sach","Tac gia","So lan muon"],rows)

    def _show_overdue(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT s.Name, s.StudentID, bk.Title, b.DueDate,
                   CAST(julianday('now')-julianday(b.DueDate) AS INTEGER) as days, b.FineAmount
            FROM Borrow b JOIN Students s ON b.StudentID=s.StudentID
            JOIN Books bk ON b.BookID=bk.BookID WHERE b.Status='Overdue' ORDER BY b.DueDate ASC
        """)
        rows = cur.fetchall(); conn.close()
        data = [(r[0],r[1],r[2],r[3],f"{r[4]} ngay",f"{r[5]:,.0f}d") for r in rows]
        self._show_table(f"Danh sach sach qua han ({len(data)} phieu)",
            ["Ho ten","Ma SV","Ten sach","Han tra","So ngay qua","Tien phat"],data)

    def _show_students(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT s.Name, s.StudentID, s.Faculty, COUNT(b.BorrowID) as total
            FROM Students s LEFT JOIN Borrow b ON s.StudentID=b.StudentID
            GROUP BY s.StudentID ORDER BY total DESC
        """)
        rows = cur.fetchall(); conn.close()
        self._show_table("Thong ke muon sach theo doc gia",
            ["Ho ten","Ma SV","Khoa","Tong luot muon"],rows)

    def _show_fines(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT s.Name, s.StudentID, b.DueDate, b.ReturnDate, b.FineAmount,
                   CASE b.FinePaid WHEN 1 THEN 'Da nop' ELSE 'Chua nop' END
            FROM Borrow b JOIN Students s ON b.StudentID=s.StudentID
            WHERE b.FineAmount>0 ORDER BY b.FineAmount DESC
        """)
        rows = cur.fetchall(); conn.close()
        data = [(r[0],r[1],r[2],r[3] or "",f"{r[4]:,.0f}d",r[5]) for r in rows]
        self._show_table(f"Bao cao tien phat ({len(data)} phieu)",
            ["Ho ten","Ma SV","Han tra","Ngay tra","Tien phat","Trang thai"],data)

    def _export_borrow(self):
        try:
            from reports.export_excel import export_borrow_report
            path, _ = QFileDialog.getSaveFileName(self,"Luu file","bao_cao_muon_tra.xlsx","Excel (*.xlsx)")
            if path: export_borrow_report(path); QMessageBox.information(self,"Thanh cong",f"Da xuat: {path}")
        except ImportError: QMessageBox.warning(self,"Thieu thu vien","pip install pandas openpyxl")
        except Exception as e: QMessageBox.critical(self,"Loi",str(e))