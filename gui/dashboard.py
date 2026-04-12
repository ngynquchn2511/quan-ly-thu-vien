import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget, QSizePolicy,
    QGraphicsDropShadowEffect, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QCursor

from config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_BG,
    COLOR_PRIMARY_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK,
    COLOR_TEXT_MID, COLOR_TEXT_MUTED, COLOR_BORDER,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, APP_NAME
)
from services.borrow_service import get_dashboard_stats, update_overdue_status


# ── Styles ─────────────────────────────────────────────────────────────────────
STYLE_SIDEBAR = f"""
    QWidget#Sidebar {{
        background: {COLOR_PRIMARY};
    }}
"""
STYLE_TOPBAR = f"""
    QWidget#Topbar {{
        background: {COLOR_WHITE};
        border-bottom: 1px solid {COLOR_BORDER};
    }}
"""
STYLE_CONTENT = f"""
    QWidget#Content {{
        background: #F4F7FE;
    }}
"""
STYLE_NAV_ITEM = f"""
    QPushButton {{
        background: transparent;
        color: rgba(255,255,255,0.8);
        border: none;
        border-left: 3px solid transparent;
        border-radius: 0px;
        text-align: left;
        padding: 10px 16px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: rgba(255,255,255,0.15);
        color: white;
    }}
"""
STYLE_NAV_ACTIVE = f"""
    QPushButton {{
        background: rgba(255,255,255,0.2);
        color: white;
        border: none;
        border-left: 3px solid white;
        border-radius: 0px;
        text-align: left;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: bold;
    }}
"""
STYLE_LOGOUT = f"""
    QPushButton {{
        background: transparent;
        color: rgba(255,255,255,0.7);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 12px;
        text-align: left;
    }}
    QPushButton:hover {{
        background: rgba(255,255,255,0.15);
        color: white;
    }}
"""
STYLE_CARD = f"""
    QFrame {{
        background: {COLOR_WHITE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
    }}
"""


# ── Avatar chữ cái ─────────────────────────────────────────────────────────────
class AvatarLabel(QWidget):
    def __init__(self, initials="", bg="#8AAAE5", fg="white", size=34, radius=17, parent=None):
        super().__init__(parent)
        self.initials = initials[:2].upper()
        self.bg = QColor(bg)
        self.fg = QColor(fg)
        self.r  = radius
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.r, self.r)
        p.fillPath(path, self.bg)
        p.setPen(self.fg)
        p.setFont(QFont("Times New Roman", 11, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, self.initials)


# ── Stat Card ──────────────────────────────────────────────────────────────────
class StatCard(QFrame):
    def __init__(self, title, value, icon_text, bg_icon, fg_icon, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE_CARD)
        self.setFixedHeight(90)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)

        icon = AvatarLabel(icon_text, bg_icon, fg_icon, 40, 8)
        lay.addWidget(icon)

        right = QVBoxLayout()
        right.setSpacing(2)
        self.lbl_val = QLabel(str(value))
        self.lbl_val.setFont(QFont("Times New Roman", 20, QFont.Bold))
        self.lbl_val.setStyleSheet(f"color: {COLOR_TEXT_DARK}; border: none;")
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; border: none;")
        right.addWidget(self.lbl_val)
        right.addWidget(self.lbl_title)
        lay.addLayout(right)
        lay.addStretch()

    def set_value(self, v):
        self.lbl_val.setText(str(v))


# ── Panel đơn giản ─────────────────────────────────────────────────────────────
class Panel(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE_CARD)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 14, 16, 14)
        self._lay.setSpacing(8)
        if title:
            lbl = QLabel(title)
            lbl.setFont(QFont("Times New Roman", 12, QFont.Bold))
            lbl.setStyleSheet(f"color: {COLOR_TEXT_DARK}; border: none;")
            self._lay.addWidget(lbl)
            div = QFrame()
            div.setFrameShape(QFrame.HLine)
            div.setStyleSheet(f"color: {COLOR_BORDER}; border: none;")
            self._lay.addWidget(div)

    def layout(self):
        return self._lay


# ── Màn hình Dashboard ─────────────────────────────────────────────────────────
class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(14)

        # Stat cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.card_books    = StatCard("Tổng số sách",    "...", "S",  "#EEF3FC", COLOR_PRIMARY)
        self.card_students = StatCard("Sinh viên",        "...", "SV", "#F0FFF4", COLOR_SUCCESS)
        self.card_borrow   = StatCard("Đang mượn",        "...", "M",  "#FFFAF0", COLOR_WARNING)
        self.card_overdue  = StatCard("Quá hạn",          "...", "!",  "#FFF5F5", COLOR_DANGER)
        for c in [self.card_books, self.card_students,
                  self.card_borrow, self.card_overdue]:
            stats_row.addWidget(c)
        lay.addLayout(stats_row)

        # Row 2: overdue list + chart placeholder
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.panel_overdue = Panel("Sách quá hạn")
        self.panel_overdue.setMinimumHeight(200)
        row2.addWidget(self.panel_overdue, 1)

        panel_top = Panel("Top sách mượn nhiều")
        panel_top.setMinimumHeight(200)
        self._fill_top_books(panel_top.layout())
        row2.addWidget(panel_top, 1)

        lay.addLayout(row2)

        # Row 3: recent activity
        panel_act = Panel("Hoạt động gần đây")
        self._fill_activity(panel_act.layout())
        lay.addWidget(panel_act)

        lay.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _fill_top_books(self, lay):
        books = [
            ("1", "Lập trình Python cơ bản",     "42 lần"),
            ("2", "Cơ sở dữ liệu quan hệ",       "38 lần"),
            ("3", "Giải thuật & CTDL",            "31 lần"),
        ]
        for rank, title, count in books:
            row = QHBoxLayout()
            av  = AvatarLabel(rank, COLOR_PRIMARY_BG, COLOR_PRIMARY, 28, 6)
            lbl = QLabel(title)
            lbl.setStyleSheet(f"color: {COLOR_TEXT_DARK}; font-size: 12px; border: none;")
            cnt = QLabel(count)
            cnt.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; border: none;")
            row.addWidget(av)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(cnt)
            lay.addLayout(row)

    def _fill_activity(self, lay):
        acts = [
            ("TT", "Thêm sách mới — Clean Code",          "09:14", "#F0FFF4", COLOR_SUCCESS),
            ("M",  "Mượn sách — SV2021001",               "08:52", "#FFFAF0", COLOR_WARNING),
            ("TR", "Trả sách — SV2020034",                "08:30", COLOR_PRIMARY_BG, COLOR_PRIMARY),
        ]
        for initials, text, time, bg, fg in acts:
            row = QHBoxLayout()
            av  = AvatarLabel(initials, bg, fg, 30, 6)
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {COLOR_TEXT_DARK}; font-size: 12px; border: none;")
            t   = QLabel(time)
            t.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; border: none;")
            row.addWidget(av)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(t)
            lay.addLayout(row)

    def refresh(self):
        try:
            stats = get_dashboard_stats()
            self.card_books.set_value(stats.get("total_books", 0))
            self.card_students.set_value(stats.get("total_students", 0))
            self.card_borrow.set_value(stats.get("borrowing", 0))
            self.card_overdue.set_value(stats.get("overdue", 0))

            # Xoa overdue cu
            lay = self.panel_overdue.layout()
            while lay.count() > 2:
                item = lay.takeAt(lay.count() - 1)
                if item.widget():
                    item.widget().deleteLater()

            from services.fine_service import get_overdue_list
            from utils.helpers import format_date, format_currency
            overdues = get_overdue_list()
            if not overdues:
                lbl = QLabel("Không có sách quá hạn")
                lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; border: none;")
                lay.addWidget(lbl)
            for od in overdues[:5]:
                row = QHBoxLayout()
                name = od.get("Name", "")
                av   = AvatarLabel(name[:2], COLOR_PRIMARY_BG, COLOR_PRIMARY, 30, 6)
                info = QVBoxLayout()
                info.setSpacing(0)
                lbl_name = QLabel(name)
                lbl_name.setStyleSheet(f"color: {COLOR_TEXT_DARK}; font-size: 12px; font-weight: bold; border: none;")
                lbl_book = QLabel(f"{od.get('Title','')} — Quá {int(od.get('OverdueDays',0))} ngày")
                lbl_book.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; border: none;")
                info.addWidget(lbl_name)
                info.addWidget(lbl_book)
                fine_lbl = QLabel(format_currency(od.get("FineAmount", 0)))
                fine_lbl.setStyleSheet(f"color: {COLOR_DANGER}; font-size: 11px; font-weight: bold; border: none;")
                row.addWidget(av)
                row.addLayout(info)
                row.addStretch()
                row.addWidget(fine_lbl)
                lay.addLayout(row)
        except Exception as e:
            print(f"[Dashboard] refresh error: {e}")


# ── Màn hình placeholder (Books, Students, Borrow, Reports, Staff) ─────────────
class PlaceholderScreen(QWidget):
    def __init__(self, title, desc="Đang xây dựng...", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Times New Roman", 18, QFont.Bold))
        lbl_t.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        lbl_t.setAlignment(Qt.AlignCenter)
        lbl_d = QLabel(desc)
        lbl_d.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_d.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_t)
        lay.addSpacing(8)
        lay.addWidget(lbl_d)


# ── Nav button ─────────────────────────────────────────────────────────────────
class NavButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(STYLE_NAV_ITEM)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCheckable(False)

    def set_active(self, active: bool):
        self.setStyleSheet(STYLE_NAV_ACTIVE if active else STYLE_NAV_ITEM)


# ── Section label trong sidebar ────────────────────────────────────────────────
def sidebar_section(text):
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        "color: rgba(255,255,255,0.5); font-size: 10px;"
        "font-weight: bold; letter-spacing: 1px; padding: 10px 16px 3px 16px;"
    )
    return lbl


# ── Dashboard Window chính ─────────────────────────────────────────────────────
class DashboardWindow(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.setWindowTitle(APP_NAME)
        self.resize(1150, 700)
        self.setMinimumSize(900, 600)
        self._nav_buttons = {}
        self._current_page = "dashboard"
        self._build_ui()
        self._center()
        # Cap nhat trang thai qua han khi mo app
        try:
            update_overdue_status()
        except Exception:
            pass
        self._show_page("dashboard")

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SIDEBAR ───────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setStyleSheet(STYLE_SIDEBAR)
        sidebar.setFixedWidth(210)
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)

        # Logo + tên app
        logo_area = QWidget()
        logo_area.setStyleSheet(f"border-bottom: 1px solid rgba(255,255,255,0.2);")
        logo_inner = QVBoxLayout(logo_area)
        logo_inner.setContentsMargins(16, 18, 16, 14)
        logo_inner.setSpacing(6)

        logo_row = QHBoxLayout()
        logo_icon = AvatarLabel("LB", COLOR_WHITE, COLOR_PRIMARY, 34, 8)
        lbl_app = QLabel(APP_NAME)
        lbl_app.setFont(QFont("Times New Roman", 11, QFont.Bold))
        lbl_app.setStyleSheet("color: white; border: none;")
        lbl_app.setWordWrap(True)
        logo_row.addWidget(logo_icon)
        logo_row.addSpacing(8)
        logo_row.addWidget(lbl_app)
        logo_row.addStretch()
        logo_inner.addLayout(logo_row)
        sb_lay.addWidget(logo_area)

        # Nav items
        nav_area = QWidget()
        nav_lay  = QVBoxLayout(nav_area)
        nav_lay.setContentsMargins(0, 6, 0, 6)
        nav_lay.setSpacing(0)

        pages = [
            ("tong_quan",  "Tổng quan",   [("dashboard", "  Dashboard")]),
            ("quan_ly",    "Quản lý",     [
                ("books",    "  Quản lý Sách"),
                ("students", "  Độc giả"),
                ("borrow",   "  Mượn / Trả"),
            ]),
            ("he_thong",   "Hệ thống",   [
                ("reports",  "  Báo cáo"),
                ("staff",    "  Nhân viên"),
            ]),
        ]

        for _, section_name, items in pages:
            nav_lay.addWidget(sidebar_section(section_name))
            for key, label in items:
                btn = NavButton(label)
                btn.clicked.connect(lambda _, k=key: self._show_page(k))
                nav_lay.addWidget(btn)
                self._nav_buttons[key] = btn

        nav_lay.addStretch()
        sb_lay.addWidget(nav_area)

        # User info + logout
        footer = QWidget()
        footer.setStyleSheet(f"border-top: 1px solid rgba(255,255,255,0.2);")
        footer_lay = QVBoxLayout(footer)
        footer_lay.setContentsMargins(12, 10, 12, 12)
        footer_lay.setSpacing(6)

        name = self.current_user.get("Name", "User")
        role = self.current_user.get("Role", "staff")
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "AD"

        user_row = QHBoxLayout()
        av = AvatarLabel(initials, "rgba(255,255,255,0.25)", "white", 32, 16)
        av.setStyleSheet("background: rgba(255,255,255,0.25); border-radius: 16px;")
        user_info = QVBoxLayout()
        user_info.setSpacing(0)
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("color: rgba(255,255,255,0.95); font-size: 12px; border: none;")
        lbl_role = QLabel("Quản trị viên" if role == "admin" else "Nhân viên")
        lbl_role.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 10px; border: none;")
        user_info.addWidget(lbl_name)
        user_info.addWidget(lbl_role)
        user_row.addWidget(av)
        user_row.addSpacing(6)
        user_row.addLayout(user_info)
        footer_lay.addLayout(user_row)

        btn_logout = QPushButton("  Đăng xuất")
        btn_logout.setStyleSheet(STYLE_LOGOUT)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setFixedHeight(32)
        btn_logout.clicked.connect(self._logout)
        footer_lay.addWidget(btn_logout)

        sb_lay.addWidget(footer)
        root.addWidget(sidebar)

        # ── MAIN AREA ─────────────────────────────────────────────────────────
        main_area = QWidget()
        main_area.setObjectName("Content")
        main_area.setStyleSheet(STYLE_CONTENT)
        main_lay = QVBoxLayout(main_area)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # Topbar
        topbar = QWidget()
        topbar.setObjectName("Topbar")
        topbar.setStyleSheet(STYLE_TOPBAR)
        topbar.setFixedHeight(52)
        tb_lay = QHBoxLayout(topbar)
        tb_lay.setContentsMargins(20, 0, 20, 0)

        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setFont(QFont("Times New Roman", 14, QFont.Bold))
        self.lbl_page_title.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        tb_lay.addWidget(self.lbl_page_title)
        tb_lay.addStretch()

        # Badge quá hạn
        self.badge_overdue = QLabel("  0 quá hạn  ")
        self.badge_overdue.setStyleSheet(
            f"background: {COLOR_DANGER}; color: white;"
            "border-radius: 10px; font-size: 11px; font-weight: bold; padding: 2px 6px;"
        )
        self.badge_overdue.hide()
        tb_lay.addWidget(self.badge_overdue)

        main_lay.addWidget(topbar)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        from gui.book_gui import BookWindow
        self.screens = {
            "dashboard": DashboardScreen(),
            "books":     BookWindow(),
            "students":  PlaceholderScreen("Quản lý Độc giả", "Sẽ được xây dựng ở bước tiếp theo"),
            "borrow":    PlaceholderScreen("Mượn / Trả Sách", "Sẽ được xây dựng ở bước tiếp theo"),
            "reports":   PlaceholderScreen("Báo cáo",         "Sẽ được xây dựng ở bước tiếp theo"),
            "staff":     PlaceholderScreen("Nhân viên",       "Sẽ được xây dựng ở bước tiếp theo"),
        }
        for screen in self.screens.values():
            self.stack.addWidget(screen)

        main_lay.addWidget(self.stack)
        root.addWidget(main_area)

    # ── Chuyển trang ──────────────────────────────────────────────────────────
    PAGE_TITLES = {
        "dashboard": "Dashboard",
        "books":     "Quản lý Sách",
        "students":  "Quản lý Độc giả",
        "borrow":    "Mượn / Trả Sách",
        "reports":   "Báo cáo & Thống kê",
        "staff":     "Quản lý Nhân viên",
    }

    def _show_page(self, key: str):
        self._current_page = key
        self.stack.setCurrentWidget(self.screens[key])
        self.lbl_page_title.setText(self.PAGE_TITLES.get(key, key))

        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

        if key == "dashboard":
            self.screens["dashboard"].refresh()
            try:
                from services.borrow_service import get_dashboard_stats
                stats = get_dashboard_stats()
                od = stats.get("overdue", 0)
                if od > 0:
                    self.badge_overdue.setText(f"  {od} quá hạn  ")
                    self.badge_overdue.show()
                else:
                    self.badge_overdue.hide()
            except Exception:
                pass

    # ── Đăng xuất ─────────────────────────────────────────────────────────────
    def _logout(self):
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Đăng xuất",
            "Bạn có chắc muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from gui.login_gui import LoginWindow
            self.login = LoginWindow()
            self.login.show()
            self.close()

    # ── Căn giữa ──────────────────────────────────────────────────────────────
    def _center(self):
        from PyQt5.QtWidgets import QDesktopWidget
        geo = QDesktopWidget().screenGeometry()
        self.move(
            (geo.width()  - self.width())  // 2,
            (geo.height() - self.height()) // 2,
        )