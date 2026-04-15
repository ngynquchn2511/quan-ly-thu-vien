import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thu Vien - Sinh Vien")
        self.resize(400, 300)
        lay = QVBoxLayout(self)
        lbl = QLabel("Man hinh dang nhap sinh vien\n(Dang xay dung...)")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
