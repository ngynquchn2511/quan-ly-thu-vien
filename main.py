"""
ENTRY POINT CHINH
Chay gop:   python main.py
Chay admin: python main.py admin
Chay user:  python main.py user
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from database.db import init_database

def main():
    init_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 14))

    mode = sys.argv[1] if len(sys.argv) > 1 else None

    if mode == "admin":
        import core.styles as styles
        app.setStyleSheet(styles.APP_STYLE + styles.MSGBOX)
        from admin_app.gui.login_gui import LoginWindow
        window = LoginWindow()
    elif mode == "user":
        from user_app.gui.login_gui import LoginWindow
        window = LoginWindow()
    else:
        # Unified login (gộp cả admin + user)
        from shared.login_gui import UnifiedLoginWindow
        window = UnifiedLoginWindow()

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
