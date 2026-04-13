import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from database.db import init_database
from gui.login_gui import LoginWindow


def main():
    init_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Font mac dinh toan app
    font = QFont("Times New Roman", 24)
    app.setFont(font)

    # Ep tat ca stylesheet dung font nay
    app.setStyleSheet("""
        * {
            font-family: 'Times New Roman';
            font-size: 24px;
        }
    """)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()