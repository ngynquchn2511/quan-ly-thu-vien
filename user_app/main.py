import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from database.db import init_database
from user_app.gui.login_gui import LoginWindow
import core.styles as styles

def main():
    init_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 14))
    app.setStyleSheet(styles.APP_STYLE)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
