import sys, os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QDesktopWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath

import core.styles as styles
from core.config import APP_NAME

class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, 60, 60, 14, 14)
        p.fillPath(path, QColor(styles.PRIMARY))
        
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("white"))
        p.drawRoundedRect(14, 12, 28, 36, 3, 3)
        p.setBrush(QColor(styles.PRIMARY_DARK))
        p.drawRect(10, 12, 6, 36)
        p.setPen(QColor(styles.PRIMARY))
        for y in [20, 26, 32, 38]:
            p.drawLine(18, y, 36, y)

class LoginWindow(QWidget):
    def __init__(self, auth_handler, title=APP_NAME, subtitle="Hệ thống quản lý thư viện"):
        super().__init__()
        self.auth_handler = auth_handler
        self.setObjectName("LoginWindow")
        self.setWindowTitle(title)
        self.setFixedSize(500, 540)
        self.setStyleSheet(f"QWidget#LoginWindow {{ background: {styles.BG}; }}")
        self._build_ui(title, subtitle)
        self._center()

    def _build_ui(self, title, subtitle):
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
        self.card.setFixedWidth(420)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(0)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignCenter)
        logo_row.addWidget(LogoWidget())
        lay.addLayout(logo_row)
        lay.addSpacing(16)

        # Title
        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet(f"color: {styles.TEXT_DARK}; border: none;")
        lay.addWidget(t)
        lay.addSpacing(4)

        s = QLabel(subtitle)
        s.setAlignment(Qt.AlignCenter)
        s.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
        lay.addWidget(s)
        lay.addSpacing(24)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {styles.BORDER}; max-height: 1px; border: none;")
        lay.addWidget(div)
        lay.addSpacing(24)

        # Fields
        lay.addWidget(self._field_label("Tài khoản"))
        lay.addSpacing(6)
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("Nhập tên đăng nhập...")
        self.inp_user.setStyleSheet(styles.INPUT)
        self.inp_user.setFixedHeight(44)
        lay.addWidget(self.inp_user)
        lay.addSpacing(16)

        lay.addWidget(self._field_label("Mật khẩu"))
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
            color: {styles.DANGER}; background: {styles.DANGER_BG};
            border: 1px solid #FECACA; border-radius: 8px;
            padding: 8px 12px; font-size: 12px;
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

        # Events
        self.btn.clicked.connect(self._on_login_click)
        self.inp_pass.returnPressed.connect(self._on_login_click)
        self.inp_user.returnPressed.connect(lambda: self.inp_pass.setFocus())
        self.inp_user.textChanged.connect(self.lbl_err.hide)
        self.inp_pass.textChanged.connect(self.lbl_err.hide)

    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {styles.TEXT_MID}; font-weight: 600; font-size: 13px; border: none;")
        return lbl

    def _on_login_click(self):
        u = self.inp_user.text().strip()
        p = self.inp_pass.text()
        if not u:
            self.show_error("Vui lòng nhập tên tài khoản"); self.inp_user.setFocus(); return
        if not p:
            self.show_error("Vui lòng nhập mật khẩu"); self.inp_pass.setFocus(); return
        
        # Call the external handler
        self.auth_handler(u, p)

    def show_error(self, msg):
        self.lbl_err.setText(msg); self.lbl_err.show()
        self._shake()

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
