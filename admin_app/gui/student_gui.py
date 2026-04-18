import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDialog, QMessageBox, QAbstractItemView, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from core.services.student_service import (
    get_all_students, add_student, update_student,
    delete_student, get_student_by_id, get_faculties
)
from database.models import Student
from database.db import get_connection
from datetime import datetime
import core.styles as styles


class StudentDialog(QDialog):
    def __init__(self, parent=None, student_data=None):
        super().__init__(parent)
        self.student_data = student_data
        self.setWindowTitle("Thêm độc giả" if not student_data else "Chỉnh sửa thông tin")
        self.setFixedSize(640, 620)
        self.setStyleSheet(f"QDialog {{ background: {styles.WHITE}; }}")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        title = QLabel("Thêm độc giả mới" if not self.student_data else "Chỉnh sửa thông tin độc giả")
        title.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: bold; font-size: 16px;")
        lay.addWidget(title)
        lay.addWidget(styles.section_divider())

        def lbl(t): return styles.field_label(t)

        # Row 1: Ma SV + Ho ten
        r1 = QHBoxLayout(); r1.setSpacing(16)
        c1 = QVBoxLayout(); c1.setSpacing(6)
        c1.addWidget(lbl("Mã sinh viên *"))
        self.inp_id = QLineEdit()
        self.inp_id.setPlaceholderText("SV2024001...")
        self.inp_id.setFixedHeight(42)
        self.inp_id.setStyleSheet(styles.INPUT)
        c1.addWidget(self.inp_id)
        c2 = QVBoxLayout(); c2.setSpacing(6)
        c2.addWidget(lbl("Họ tên *"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nguyễn Văn A...")
        self.inp_name.setFixedHeight(42)
        self.inp_name.setStyleSheet(styles.INPUT)
        c2.addWidget(self.inp_name)
        r1.addLayout(c1); r1.addLayout(c2)
        lay.addLayout(r1)

        # Row 2: Khoa + Lop
        r2 = QHBoxLayout(); r2.setSpacing(16)
        c3 = QVBoxLayout(); c3.setSpacing(6)
        c3.addWidget(lbl("Khoa"))
        self.inp_fac = QComboBox()
        self.inp_fac.setFixedHeight(42)
        self.inp_fac.setStyleSheet(styles.COMBO)
        self.inp_fac.addItems(["CNTT", "Kinh tế", "Cơ điện",
                               "Ngoại ngữ", "Khoa học", "Khác"])
        c3.addWidget(self.inp_fac)
        c4 = QVBoxLayout(); c4.setSpacing(6)
        c4.addWidget(lbl("Lớp"))
        self.inp_class = QLineEdit()
        self.inp_class.setPlaceholderText("IT21A...")
        self.inp_class.setFixedHeight(42)
        self.inp_class.setStyleSheet(styles.INPUT)
        c4.addWidget(self.inp_class)
        r2.addLayout(c3); r2.addLayout(c4)
        lay.addLayout(r2)

        # Row 3: SDT + Email
        r3 = QHBoxLayout(); r3.setSpacing(16)
        c5 = QVBoxLayout(); c5.setSpacing(6)
        c5.addWidget(lbl("Số điện thoại"))
        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("09xxxxxxxx...")
        self.inp_phone.setFixedHeight(42)
        self.inp_phone.setStyleSheet(styles.INPUT)
        c5.addWidget(self.inp_phone)
        c6 = QVBoxLayout(); c6.setSpacing(6)
        c6.addWidget(lbl("Email"))
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("sv@email.com...")
        self.inp_email.setFixedHeight(42)
        self.inp_email.setStyleSheet(styles.INPUT)
        c6.addWidget(self.inp_email)
        r3.addLayout(c5); r3.addLayout(c6)
        lay.addLayout(r3)

        lay.addWidget(lbl("Hạn thẻ thư viện"))
        self.inp_expire = QDateEdit()
        self.inp_expire.setFixedHeight(42)
        self.inp_expire.setStyleSheet(styles.INPUT)
        self.inp_expire.setCalendarPopup(True)
        self.inp_expire.setDate(QDate.currentDate().addYears(2))
        self.inp_expire.setDisplayFormat("dd/MM/yyyy")
        lay.addWidget(self.inp_expire)

        # Row 4: Account (Username + Password)
        r4 = QHBoxLayout(); r4.setSpacing(16)
        c7 = QVBoxLayout(); c7.setSpacing(6)
        c7.addWidget(lbl("Tên đăng nhập *"))
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("Tên tài khoản...")
        self.inp_user.setFixedHeight(42)
        self.inp_user.setStyleSheet(styles.INPUT)
        c7.addWidget(self.inp_user)
        c8 = QVBoxLayout(); c8.setSpacing(6)
        c8.addWidget(lbl("Mật khẩu" + ("" if self.student_data else " *")))
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Để trống nếu không đổi..." if self.student_data else "Nhập mật khẩu...")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setFixedHeight(42)
        self.inp_pass.setStyleSheet(styles.INPUT)
        c8.addWidget(self.inp_pass)
        r4.addLayout(c7); r4.addLayout(c8)
        lay.addLayout(r4)

        # Dien san neu la sua
        if self.student_data:
            self.inp_id.setText(self.student_data.get("StudentID", ""))
            self.inp_id.setEnabled(False)
            self.inp_name.setText(self.student_data.get("Name", ""))
            idx = self.inp_fac.findText(self.student_data.get("Faculty", ""))
            if idx >= 0: self.inp_fac.setCurrentIndex(idx)
            self.inp_class.setText(self.student_data.get("Class", "") or "")
            self.inp_phone.setText(self.student_data.get("Phone", "") or "")
            self.inp_email.setText(self.student_data.get("Email", "") or "")
            exp = self.student_data.get("CardExpire", "")
            if exp:
                d = QDate.fromString(exp, "yyyy-MM-dd")
                if d.isValid(): self.inp_expire.setDate(d)
            self.inp_user.setText(self.student_data.get("Username", "") or "")

        lay.addStretch()

        # Buttons
        br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc = QPushButton("Huỷ")
        bc.setStyleSheet(styles.BTN_OUTLINE)
        bc.setFixedHeight(42); bc.setMinimumWidth(100)
        bc.clicked.connect(self.reject)
        bs = QPushButton("Lưu lại")
        bs.setStyleSheet(styles.BTN_PRIMARY)
        bs.setFixedHeight(42); bs.setMinimumWidth(120)
        bs.clicked.connect(self._save)
        br.addWidget(bc); br.addWidget(bs)
        lay.addLayout(br)

    def _save(self):
        sid  = self.inp_id.text().strip()
        name = self.inp_name.text().strip()
        if not sid:  QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã sinh viên."); return
        if not name: QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên."); return
        # Logic tai khoan
        user_val = self.inp_user.text().strip()
        pass_val = self.inp_pass.text()
        
        if not user_val:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập."); return
        if not self.student_data and not pass_val:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu cho tài khoản mới."); return

        s = Student(
            student_id=sid, name=name,
            faculty=self.inp_fac.currentText(),
            class_=self.inp_class.text().strip(),
            phone=self.inp_phone.text().strip(),
            email=self.inp_email.text().strip(),
            card_expire=self.inp_expire.date().toString("yyyy-MM-dd"),
            username=user_val,
            password=pass_val
        )
        try:
            if self.student_data: update_student(s)
            else: add_student(s)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")


class StudentWindow(QWidget):
    COLS = ["Mã SV", "Họ tên", "Tài khoản", "Khoa", "Lớp",
            "Số ĐT", "Hạn thẻ", "Trạng thái", "Thao tác"]

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
        self.btn_add = QPushButton("+ Thêm độc giả")
        self.btn_add.setStyleSheet(styles.BTN_PRIMARY)
        self.btn_add.setFixedHeight(40)
        self.btn_add.clicked.connect(self._add)

        self.btn_ref = QPushButton("Làm mới")
        self.btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        self.btn_ref.setFixedHeight(40)
        self.btn_ref.clicked.connect(self.refresh)

        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo tên, mã SV, SĐT...")
        self.inp_search.setStyleSheet(styles.INPUT)
        self.inp_search.setFixedHeight(40)
        self.inp_search.setMinimumWidth(240)
        self.inp_search.textChanged.connect(self._load)

        self.cmb_fac = QComboBox()
        self.cmb_fac.setStyleSheet(styles.COMBO)
        self.cmb_fac.setFixedHeight(40)
        self.cmb_fac.addItem("Tất cả khoa")
        self.cmb_fac.currentTextChanged.connect(self._load)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color: {styles.TEXT_MUTED};")

        tb.addWidget(self.btn_add); tb.addWidget(self.btn_ref)
        tb.addStretch()
        tb.addWidget(self.inp_search); tb.addWidget(self.cmb_fac)
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
        self.table.setColumnWidth(0, 110)   # Ma SV
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Ho ten
        hdr.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 110)   # Tai khoan
        hdr.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 100)   # Khoa
        hdr.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 90)    # Lop
        hdr.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 120)   # So DT
        hdr.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 110)   # Han the
        hdr.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 200)   # Trang thai
        hdr.setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 140)   # Thao tac

        lay.addWidget(self.table)
        lay.addWidget(self.lbl_count)

    def refresh(self):
        cur = self.cmb_fac.currentText()
        self.cmb_fac.blockSignals(True)
        self.cmb_fac.clear()
        self.cmb_fac.addItem("Tất cả khoa")
        for f in get_faculties():
            self.cmb_fac.addItem(f)
        idx = self.cmb_fac.findText(cur)
        self.cmb_fac.setCurrentIndex(max(0, idx))
        self.cmb_fac.blockSignals(False)
        self._load()

    def _load(self):
        kw  = self.inp_search.text().strip()
        fac = self.cmb_fac.currentText()
        if fac == "Tất cả khoa": fac = ""
        students = get_all_students(kw, fac)
        self.table.setRowCount(0)
        today = datetime.now().strftime("%Y-%m-%d")

        for i, s in enumerate(students):
            self.table.insertRow(i)
            sid    = s.get("StudentID", "")
            expire = s.get("CardExpire", "") or ""
            valid  = expire >= today if expire else False

            conn = get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM Borrow WHERE StudentID=? AND Status IN ('Borrowing','Overdue')",
                (sid,))
            borrowing = cur.fetchone()[0]
            conn.close()

            try:
                exp_disp = datetime.strptime(expire, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                exp_disp = expire

            vals = [sid, s.get("Name",""), s.get("Username","") or "---",
                    s.get("Faculty",""), s.get("Class","") or "", 
                    s.get("Phone","") or "", exp_disp]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, col, item)

            # Badge trang thai
            if valid:
                bg, fg     = styles.SUCCESS_BG, "#166534"
                badge_text = f"Hợp lệ  |  {borrowing} cuốn mượn"
            else:
                bg, fg     = styles.DANGER_BG, "#991B1B"
                badge_text = f"Hết hạn  |  {borrowing} cuốn mượn"

            bw_s = QWidget(); bl_s = QHBoxLayout(bw_s)
            bl_s.setContentsMargins(6, 4, 6, 4)
            badge = styles.make_badge(badge_text, bg, fg, 180)
            bl_s.addWidget(badge)
            self.table.setCellWidget(i, 6, bw_s)

            # Nut thao tac
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(6, 4, 6, 4); bl.setSpacing(8)
            be = QPushButton("Sửa")
            be.setStyleSheet(styles.BTN_SMALL)
            be.setFixedHeight(30); be.setFixedWidth(60)
            be.clicked.connect(lambda _, x=sid: self._edit(x))
            bd = QPushButton("Xoá")
            bd.setStyleSheet(styles.BTN_SMALL_DANGER)
            bd.setFixedHeight(30); bd.setFixedWidth(60)
            bd.clicked.connect(lambda _, x=sid: self._delete(x))
            bl.addWidget(be); bl.addWidget(bd)
            self.table.setCellWidget(i, 7, bw)
            self.table.setRowHeight(i, 50)

        self.lbl_count.setText(f"Tổng: {len(students)} độc giả")

    def _add(self):
        if StudentDialog(self).exec_() == QDialog.Accepted:
            self.refresh()

    def _edit(self, sid):
        data = get_student_by_id(sid)
        if data and StudentDialog(self, student_data=data).exec_() == QDialog.Accepted:
            self.refresh()

    def _delete(self, sid):
        if QMessageBox.question(
            self, "Xác nhận xoá",
            f"Bạn có chắc muốn xoá độc giả '{sid}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                delete_student(sid)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))