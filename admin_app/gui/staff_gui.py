import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDialog, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from services.staff_service import get_all_staff, add_staff, delete_staff
from database.models import Staff
import styles


class StaffDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Them nhan vien moi")
        self.setFixedSize(620, 500)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(32,28,32,28); lay.setSpacing(16)
        title = QLabel("Them nhan vien moi")
        title.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: bold; font-size: 16px;")
        lay.addWidget(title)
        lay.addWidget(styles.section_divider())

        def lbl(t): return styles.field_label(t)

        r1 = QHBoxLayout(); r1.setSpacing(16)
        c1 = QVBoxLayout(); c1.setSpacing(6); c1.addWidget(lbl("Ma nhan vien *"))
        self.inp_id = QLineEdit(); self.inp_id.setPlaceholderText("NV003...")
        self.inp_id.setFixedHeight(42); self.inp_id.setStyleSheet(styles.INPUT)
        c1.addWidget(self.inp_id)
        c2 = QVBoxLayout(); c2.setSpacing(6); c2.addWidget(lbl("Ho ten *"))
        self.inp_name = QLineEdit(); self.inp_name.setPlaceholderText("Nguyen Van A...")
        self.inp_name.setFixedHeight(42); self.inp_name.setStyleSheet(styles.INPUT)
        c2.addWidget(self.inp_name)
        r1.addLayout(c1); r1.addLayout(c2); lay.addLayout(r1)

        r2 = QHBoxLayout(); r2.setSpacing(16)
        c3 = QVBoxLayout(); c3.setSpacing(6); c3.addWidget(lbl("Tai khoan *"))
        self.inp_user = QLineEdit(); self.inp_user.setPlaceholderText("username...")
        self.inp_user.setFixedHeight(42); self.inp_user.setStyleSheet(styles.INPUT)
        c3.addWidget(self.inp_user)
        c4 = QVBoxLayout(); c4.setSpacing(6); c4.addWidget(lbl("Vai tro"))
        self.inp_role = QComboBox(); self.inp_role.setFixedHeight(42); self.inp_role.setStyleSheet(styles.COMBO)
        self.inp_role.addItems(["staff","admin"])
        c4.addWidget(self.inp_role)
        r2.addLayout(c3); r2.addLayout(c4); lay.addLayout(r2)

        lay.addWidget(lbl("Mat khau *"))
        self.inp_pass = QLineEdit(); self.inp_pass.setPlaceholderText("Nhap mat khau...")
        self.inp_pass.setFixedHeight(42); self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setStyleSheet(styles.INPUT); lay.addWidget(self.inp_pass)

        lay.addWidget(lbl("Nhap lai mat khau *"))
        self.inp_pass2 = QLineEdit(); self.inp_pass2.setPlaceholderText("Nhap lai...")
        self.inp_pass2.setFixedHeight(42); self.inp_pass2.setEchoMode(QLineEdit.Password)
        self.inp_pass2.setStyleSheet(styles.INPUT); lay.addWidget(self.inp_pass2)

        lay.addStretch()
        br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc = QPushButton("Huy"); bc.setStyleSheet(styles.BTN_OUTLINE); bc.setFixedHeight(42); bc.setMinimumWidth(100); bc.clicked.connect(self.reject)
        bs = QPushButton("Luu lai"); bs.setStyleSheet(styles.BTN_PRIMARY); bs.setFixedHeight(42); bs.setMinimumWidth(120); bs.clicked.connect(self._save)
        br.addWidget(bc); br.addWidget(bs); lay.addLayout(br)

    def _save(self):
        sid=self.inp_id.text().strip(); name=self.inp_name.text().strip()
        user=self.inp_user.text().strip(); pw=self.inp_pass.text(); pw2=self.inp_pass2.text()
        if not all([sid,name,user,pw]): QMessageBox.warning(self,"Loi","Nhap day du thong tin."); return
        if pw!=pw2: QMessageBox.warning(self,"Loi","Mat khau khong khop."); return
        try:
            add_staff(Staff(staff_id=sid,name=name,username=user,password=pw,role=self.inp_role.currentText()))
            self.accept()
        except Exception as e: QMessageBox.critical(self,"Loi",str(e))


class StaffWindow(QWidget):
    COLS = ["Ma NV","Ho ten","Tai khoan","Vai tro","Trang thai","Thao tac"]

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,18,24,18); lay.setSpacing(14)

        tb = QHBoxLayout(); tb.setSpacing(10)
        self.btn_add = QPushButton("+ Them nhan vien"); self.btn_add.setStyleSheet(styles.BTN_PRIMARY)
        self.btn_add.setFixedHeight(40); self.btn_add.clicked.connect(self._add)
        self.btn_ref = QPushButton("Lam moi"); self.btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        self.btn_ref.setFixedHeight(40); self.btn_ref.clicked.connect(self.refresh)
        self.lbl_count = QLabel(); self.lbl_count.setStyleSheet(f"color: {styles.TEXT_MUTED};")
        tb.addWidget(self.btn_add); tb.addWidget(self.btn_ref); tb.addStretch(); tb.addWidget(self.lbl_count)
        lay.addLayout(tb)

        info = QFrame(); info.setStyleSheet(styles.INFO_BANNER)
        il = QHBoxLayout(info); il.setContentsMargins(16,12,16,12)
        lbl_i = QLabel("Chi tai khoan Admin moi co quyen them, xoa nhan vien. Mat khau duoc ma hoa SHA-256.")
        lbl_i.setStyleSheet(f"color: {styles.TEXT_MID}; border: none;")
        il.addWidget(lbl_i); lay.addWidget(info)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.setStyleSheet(styles.TABLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        hdr = self.table.horizontalHeader()
        for c in range(3): hdr.setSectionResizeMode(c, QHeaderView.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed); self.table.setColumnWidth(3, 120)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed); self.table.setColumnWidth(4, 130)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed); self.table.setColumnWidth(5, 100)
        lay.addWidget(self.table)

    def refresh(self):
        staffs = get_all_staff(); self.table.setRowCount(0)
        cur_id = self.current_user.get("StaffID","")
        for i, s in enumerate(staffs):
            self.table.insertRow(i)
            for col, key in enumerate(["StaffID","Name","Username"]):
                item = QTableWidgetItem(s.get(key,""))
                item.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
                self.table.setItem(i, col, item)
            role = s.get("Role","staff")
            rb_bg, rb_fg = (styles.PRIMARY_LIGHT, styles.PRIMARY) if role=="admin" else (styles.WARNING_BG,"#92400E")
            self.table.setCellWidget(i, 3, styles.badge_widget("Admin" if role=="admin" else "Staff", rb_bg, rb_fg, 80))
            self.table.setCellWidget(i, 4, styles.badge_widget("Hoat dong", styles.SUCCESS_BG, "#166534", 100))
            sid = s.get("StaffID","")
            bw = QWidget(); bl = QHBoxLayout(bw); bl.setContentsMargins(6,4,6,4)
            if sid != cur_id:
                bd = QPushButton("Xoa"); bd.setStyleSheet(styles.BTN_SMALL_DANGER); bd.setFixedHeight(30)
                bd.clicked.connect(lambda _,x=sid: self._delete(x)); bl.addWidget(bd)
            self.table.setCellWidget(i, 5, bw)
            self.table.setRowHeight(i, 50)
        self.lbl_count.setText(f"Tong: {len(staffs)} nhan vien")

    def _add(self):
        if StaffDialog(self).exec_() == QDialog.Accepted: self.refresh()

    def _delete(self, sid):
        if QMessageBox.question(self,"Xac nhan",f"Xoa nhan vien '{sid}'?",
           QMessageBox.Yes|QMessageBox.No,QMessageBox.No) == QMessageBox.Yes:
            try: delete_staff(sid); self.refresh()
            except Exception as e: QMessageBox.critical(self,"Loi",str(e))