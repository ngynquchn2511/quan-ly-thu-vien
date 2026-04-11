import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from config import APP_NAME

class DashboardWindow(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 680)
        lay = QVBoxLayout(self)
        name = self.current_user.get("Name", "")
        role = self.current_user.get("Role", "")
        lbl = QLabel(f"Xin chao, {name}  |  Quyen: {role}\n\n(Dashboard dang duoc xay dung...)")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #1A2540;")
        lay.addWidget(lbl)
