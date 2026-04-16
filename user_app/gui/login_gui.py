import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
    QDesktopWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath

from core.services.staff_service import authenticate
from core.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_BG,
    COLOR_WHITE, COLOR_TEXT_DARK, COLOR_TEXT_MID,
    COLOR_TEXT_MUTED, COLOR_BORDER, APP_NAME
)

# ── Styles ────────────────────────────────────────────────────────────────────
STYLE_WINDOW = f"""
    QWidget#LoginWindow {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLOR_PRIMARY_BG}, stop:1 {COLOR_WHITE}
        );
    }}
"""
STYLE_CARD = f"""
    QFrame#LoginCard {{
        background: {COLOR_WHITE};
        border-radius: 16px;
        border: 1px solid {COLOR_BORDER};
    }}
"""
STYLE_INPUT = f"""
    QLineEdit {{
        background: {COLOR_PRIMARY_BG};
        border: 1.5px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        color: {COLOR_TEXT_DARK};
    }}
    QLineEdit:focus {{
        border: 1.5px solid {COLOR_PRIMARY};
        background: {COLOR_WHITE};
    }}
    QLineEdit:hover {{
        border: 1.5px solid {COLOR_PRIMARY};
    }}
"""
STYLE_BTN = f"""
    QPushButton {{
        background: {COLOR_PRIMARY};
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        padding: 11px;
    }}
    QPushButton:hover   {{ background: {COLOR_PRIMARY_DARK}; }}
    QPushButton:pressed {{ background: #5A7BC4; }}
"""
STYLE_ERROR = """
    QLabel {
        color: #C53030;
        background: #FFF5F5;
        border: 1px solid #FEB2B2;
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 12px;
    }
"""


# ── Logo widget ───────────────────────────────────────────────────────────────
class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, 60, 60, 13, 13)
        p.fillPath(path, QColor(COLOR_PRIMARY))
        # Sach
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("white"))
        p.drawRoundedRect(13, 11, 26, 34, 3, 3)
        p.setBrush(QColor(COLOR_PRIMARY_DARK))
        p.drawRect(10, 11, 5, 34)
        p.setPen(QColor(COLOR_PRIMARY))
        for y in [19, 24, 29, 34]:
            p.drawLine(17, y, 35, y)


# ── Login Window ──────────────────────────────────────────────────────────────
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(500, 520)
        self.setStyleSheet(STYLE_WINDOW)
        self._build_ui()
        self._center()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(36, 36, 36, 36)

        # Card
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setStyleSheet(STYLE_CARD)
        self.card.setFixedWidth(420)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(138, 170, 229, 55))
        self.card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(0)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignCenter)
        logo_row.addWidget(LogoWidget())
        lay.addLayout(logo_row)
        lay.addSpacing(12)

        # Tieu de
        t = QLabel(APP_NAME)
        t.setAlignment(Qt.AlignCenter)
        t.setFont(QFont("Segoe UI", 14, QFont.Bold))
        t.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        lay.addWidget(t)
        lay.addSpacing(3)

        s = QLabel("Hệ thống quản lý thư viện")
        s.setAlignment(Qt.AlignCenter)
        s.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        lay.addWidget(s)
        lay.addSpacing(22)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {COLOR_BORDER};")
        lay.addWidget(div)
        lay.addSpacing(20)

        # Username
        lay.addWidget(self._field_label("Tài khoản"))
        lay.addSpacing(5)
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("Nhập tên đăng nhập")
        self.inp_user.setStyleSheet(STYLE_INPUT)
        self.inp_user.setFixedHeight(42)
        lay.addWidget(self.inp_user)
        lay.addSpacing(13)

        # Password
        lay.addWidget(self._field_label("Mật khẩu"))
        lay.addSpacing(5)
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Nhập mật khẩu...")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setStyleSheet(STYLE_INPUT)
        self.inp_pass.setFixedHeight(42)
        lay.addWidget(self.inp_pass)
        lay.addSpacing(5)

        # Error label (an mac dinh)
        self.lbl_err = QLabel()
        self.lbl_err.setStyleSheet(STYLE_ERROR)
        self.lbl_err.setAlignment(Qt.AlignCenter)
        self.lbl_err.setWordWrap(True)
        self.lbl_err.hide()
        lay.addWidget(self.lbl_err)
        lay.addSpacing(16)

        # Button
        self.btn = QPushButton("Đăng nhập")
        self.btn.setStyleSheet(STYLE_BTN)
        self.btn.setFixedHeight(44)
        self.btn.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.btn)

        outer.addWidget(self.card)

        # Events
        self.btn.clicked.connect(self._login)
        self.inp_pass.returnPressed.connect(self._login)
        self.inp_user.returnPressed.connect(lambda: self.inp_pass.setFocus())
        self.inp_user.textChanged.connect(self.lbl_err.hide)
        self.inp_pass.textChanged.connect(self.lbl_err.hide)

    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MID}; font-size: 11px;"
            "font-weight: bold; letter-spacing: 0.5px;"
        )
        return lbl

    # ── Logic đăng nhập ───────────────────────────────────────────────────────
    def _login(self):
        username = self.inp_user.text().strip()
        password = self.inp_pass.text()

        if not username:
            self._err("Vui lòng nhập tên tài khoản.")
            self.inp_user.setFocus()
            return
        if not password:
            self._err("Vui lòng nhập mật khẩu.")
            self.inp_pass.setFocus()
            return

        # 1. Thử đăng nhập Staff trước
        user = authenticate(username, password)
        if user:
            from user_app.gui.dashboard import DashboardWindow
            self.dashboard = DashboardWindow(current_user=user)
            self.dashboard.show()
            self.close()
            return

        # 2. Thử đăng nhập Student
        from core.services.student_service import authenticate_student
        student = authenticate_student(username, password)
        if student:
            from user_app.gui.student_gui import StudentPortalWindow
            self.portal = StudentPortalWindow(current_student=student)
            self.portal.show()
            self.close()
            return

        # 3. Sai tài khoản
        self._err("Tài khoản hoặc mật khẩu không chính xác.")
        self.inp_pass.clear()
        self.inp_pass.setFocus()
        self._shake()

    def _err(self, msg):
        self.lbl_err.setText(msg)
        self.lbl_err.show()

    # ── Hieu ung lac khi sai ─────────────────────────────────────────────────
    def _shake(self):
        pos = self.card.pos()
        x, y = pos.x(), pos.y()
        self._anim = QPropertyAnimation(self.card, b"pos")
        self._anim.setDuration(280)
        for t, dx in [(0, 0), (0.15, -8), (0.35, 8),
                      (0.55, -5), (0.75, 5), (1.0, 0)]:
            self._anim.setKeyValueAt(t, QPoint(x + dx, y))
        self._anim.setEasingCurve(QEasingCurve.Linear)
        self._anim.start()

    def _center(self):
        geo = QDesktopWidget().screenGeometry()
        self.move(
            (geo.width()  - self.width())  // 2,
            (geo.height() - self.height()) // 2,
        )