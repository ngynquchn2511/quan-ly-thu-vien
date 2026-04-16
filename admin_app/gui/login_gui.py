import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QDesktopWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath

from core.services.staff_service import authenticate
from core.config import APP_NAME
import core.styles as styles


class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(56, 56)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, 56, 56, 12, 12)
        p.fillPath(path, QColor(styles.PRIMARY))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("white"))
        p.drawRoundedRect(12, 10, 24, 32, 3, 3)
        p.setBrush(QColor(styles.PRIMARY_DARK))
        p.drawRect(9, 10, 5, 32)
        p.setPen(QColor(styles.PRIMARY))
        for y in [18, 23, 28, 33]:
            p.drawLine(15, y, 33, y)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(520, 560)
        self.setStyleSheet(f"QWidget#LoginWindow {{ background: {styles.BG}; }}")
        self._build()
        self._center()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(40, 40, 40, 40)

        # Card
        self.card = QFrame()
        self.card.setStyleSheet(f"""
            QFrame {{
                background: {styles.WHITE};
                border: 1px solid {styles.BORDER};
                border-radius: 16px;
            }}
        """)
        self.card.setFixedWidth(440)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(0)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignCenter)
        logo_row.addWidget(LogoWidget())
        lay.addLayout(logo_row)
        lay.addSpacing(16)

        # Title
        t = QLabel(APP_NAME)
        t.setAlignment(Qt.AlignCenter)
        t.setFont(QFont("Segoe UI", 16, QFont.Bold))
        t.setStyleSheet(f"color: {styles.TEXT_DARK}; border: none;")
        t.setWordWrap(True)
        lay.addWidget(t)
        lay.addSpacing(4)

        s = QLabel("Hệ thống quản lý thư viện")
        s.setAlignment(Qt.AlignCenter)
        s.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
        lay.addWidget(s)
        lay.addSpacing(28)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {styles.BORDER}; max-height: 1px; border: none;")
        lay.addWidget(div)
        lay.addSpacing(24)

        # Username
        lbl_u = QLabel("Tai khoan")
        lbl_u.setStyleSheet(f"color: {styles.TEXT_MID}; font-weight: 600; border: none;")
        lay.addWidget(lbl_u)
        lay.addSpacing(6)
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("Nhập tên đăng nhập...")
        self.inp_user.setStyleSheet(styles.INPUT)
        self.inp_user.setFixedHeight(44)
        lay.addWidget(self.inp_user)
        lay.addSpacing(16)

        # Password
        lbl_p = QLabel("Mat khau")
        lbl_p.setStyleSheet(f"color: {styles.TEXT_MID}; font-weight: 600; border: none;")
        lay.addWidget(lbl_p)
        lay.addSpacing(6)
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Nhập mật khẩu...")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setStyleSheet(styles.INPUT)
        self.inp_pass.setFixedHeight(44)
        lay.addWidget(self.inp_pass)
        lay.addSpacing(8)

        # Error
        self.lbl_err = QLabel()
        self.lbl_err.setStyleSheet(f"""
            color: {styles.DANGER};
            background: {styles.DANGER_BG};
            border: 1px solid #FECACA;
            border-radius: 8px;
            padding: 8px 12px;
        """)
        self.lbl_err.setAlignment(Qt.AlignCenter)
        self.lbl_err.setWordWrap(True)
        self.lbl_err.hide()
        lay.addWidget(self.lbl_err)
        lay.addSpacing(20)

        # Button
        self.btn = QPushButton("Đăng nhập")
        self.btn.setStyleSheet(styles.BTN_PRIMARY)
        self.btn.setFixedHeight(46)
        self.btn.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.btn)

        outer.addWidget(self.card)

        self.btn.clicked.connect(self._login)
        self.inp_pass.returnPressed.connect(self._login)
        self.inp_user.returnPressed.connect(lambda: self.inp_pass.setFocus())
        self.inp_user.textChanged.connect(self.lbl_err.hide)
        self.inp_pass.textChanged.connect(self.lbl_err.hide)

    def _login(self):
        username = self.inp_user.text().strip()
        password = self.inp_pass.text()
        if not username:
            self._err("Vui lòng nhập tên tài khoản")
            self.inp_user.setFocus(); return
        if not password:
            self._err("Vui lòng nhập mật khẩu")
            self.inp_pass.setFocus(); return
        user = authenticate(username, password)
        if user is None:
            self._err("Tài khoản hoặc mật khẩu không chính xác.")
            self.inp_pass.clear(); self.inp_pass.setFocus()
            self._shake(); return
        from gui.dashboard import DashboardWindow
        self.dashboard = DashboardWindow(current_user=user)
        self.dashboard.show(); self.close()

    def _err(self, msg):
        self.lbl_err.setText(msg); self.lbl_err.show()

    def _shake(self):
        pos = self.card.pos(); x, y = pos.x(), pos.y()
        self._anim = QPropertyAnimation(self.card, b"pos")
        self._anim.setDuration(300)
        for t, dx in [(0,0),(0.15,-10),(0.35,10),(0.55,-6),(0.75,6),(1.0,0)]:
            self._anim.setKeyValueAt(t, QPoint(x+dx, y))
        self._anim.setEasingCurve(QEasingCurve.Linear)
        self._anim.start()

    def _center(self):
        geo = QDesktopWidget().screenGeometry()
        self.move((geo.width()-self.width())//2, (geo.height()-self.height())//2)