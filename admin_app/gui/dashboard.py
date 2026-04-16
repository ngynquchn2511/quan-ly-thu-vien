import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QSizePolicy, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath

from core.config import APP_NAME
from core.services.borrow_service import get_dashboard_stats, update_overdue_status
import core.styles as styles


class AvatarLabel(QWidget):
    def __init__(self, initials="", bg=None, fg="white", size=36, radius=18, parent=None):
        super().__init__(parent)
        self.initials = initials[:2].upper()
        self.bg = QColor(bg or styles.PRIMARY)
        self.fg = QColor(fg)
        self.r = radius
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.r, self.r)
        p.fillPath(path, self.bg); p.setPen(self.fg)
        p.setFont(QFont("Segoe UI", 11, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, self.initials)


class StatCard(QFrame):
    def __init__(self, title, value, icon, icon_bg, icon_fg, parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.CARD)
        self.setFixedHeight(100)
        lay = QHBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(16)
        av = AvatarLabel(icon, icon_bg, icon_fg, 44, 10)
        lay.addWidget(av)
        right = QVBoxLayout(); right.setSpacing(4)
        self.lbl_val = QLabel(str(value))
        self.lbl_val.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.lbl_val.setStyleSheet(f"color: {styles.TEXT_DARK}; border: none;")
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
        right.addWidget(self.lbl_val); right.addWidget(self.lbl_title)
        lay.addLayout(right); lay.addStretch()

    def set_value(self, v): self.lbl_val.setText(str(v))


class Panel(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.CARD)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(20,16,20,16); self._lay.setSpacing(10)
        if title:
            lbl = QLabel(title)
            lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
            lbl.setStyleSheet(f"color: {styles.TEXT_DARK}; border: none;")
            self._lay.addWidget(lbl)
            div = QFrame(); div.setFrameShape(QFrame.HLine)
            div.setStyleSheet(f"background: {styles.BORDER}; max-height: 1px; border: none;")
            self._lay.addWidget(div)

    def layout(self): return self._lay


class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build()

    def _build(self):
        scroll = QScrollArea(self); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        lay = QVBoxLayout(container); lay.setContentsMargins(24,24,24,24); lay.setSpacing(16)

        # Stat cards
        stats_row = QHBoxLayout(); stats_row.setSpacing(14)
        self.card_books    = StatCard("Tổng số sách",  "...", "S",  styles.PRIMARY_LIGHT, styles.PRIMARY)
        self.card_students = StatCard("Sinh viên",      "...", "SV", styles.SUCCESS_BG,    styles.SUCCESS)
        self.card_borrow   = StatCard("Đang mượn",      "...", "M",  styles.WARNING_BG,    styles.WARNING)
        self.card_overdue  = StatCard("Quá hạn",        "...", "!",  styles.DANGER_BG,     styles.DANGER)
        for c in [self.card_books, self.card_students, self.card_borrow, self.card_overdue]:
            stats_row.addWidget(c)
        lay.addLayout(stats_row)

        row2 = QHBoxLayout(); row2.setSpacing(14)
        self.panel_overdue = Panel("Sách quá hạn")
        self.panel_overdue.setMinimumHeight(220)
        panel_top = Panel("Top sách mượn nhiều")
        panel_top.setMinimumHeight(220)
        self._fill_top(panel_top.layout())
        row2.addWidget(self.panel_overdue, 1); row2.addWidget(panel_top, 1)
        lay.addLayout(row2)

        panel_act = Panel("Hoạt động gần đây")
        self._fill_activity(panel_act.layout())
        lay.addWidget(panel_act)
        lay.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

    def _fill_top(self, lay):
        books = [
            ("1", "Lập trình Python cơ bản",       "42 lần"),
            ("2", "Cơ sở dữ liệu quan hệ",         "38 lần"),
            ("3", "Giải thuật & Cấu trúc dữ liệu", "31 lần"),
        ]
        for rank, title, count in books:
            row = QHBoxLayout(); row.setSpacing(10)
            av  = AvatarLabel(rank, styles.PRIMARY_LIGHT, styles.PRIMARY, 30, 8)
            lbl = QLabel(title); lbl.setStyleSheet(f"color: {styles.TEXT_DARK}; border: none;")
            cnt = QLabel(count); cnt.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
            row.addWidget(av); row.addWidget(lbl); row.addStretch(); row.addWidget(cnt)
            lay.addLayout(row)

    def _fill_activity(self, lay):
        acts = [
            ("TT", "Thêm sách mới — Clean Code",   "09:14", styles.SUCCESS_BG,    styles.SUCCESS),
            ("M",  "Mượn sách — SV2021001",         "08:52", styles.WARNING_BG,    styles.WARNING),
            ("TR", "Trả sách — SV2020034",          "08:30", styles.PRIMARY_LIGHT, styles.PRIMARY),
        ]
        for ini, text, time, bg, fg in acts:
            row = QHBoxLayout(); row.setSpacing(10)
            av  = AvatarLabel(ini, bg, fg, 32, 8)
            lbl = QLabel(text); lbl.setStyleSheet(f"color: {styles.TEXT_DARK}; border: none;")
            t   = QLabel(time); t.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
            row.addWidget(av); row.addWidget(lbl); row.addStretch(); row.addWidget(t)
            lay.addLayout(row)

    def refresh(self):
        try:
            stats = get_dashboard_stats()
            self.card_books.set_value(stats.get("total_books", 0))
            self.card_students.set_value(stats.get("total_students", 0))
            self.card_borrow.set_value(stats.get("borrowing", 0))
            self.card_overdue.set_value(stats.get("overdue", 0))

            # Xoa noi dung cu cua panel overdue
            # Xay dung lai panel tu dau
            lay = self.panel_overdue.layout()

            # Xoa het item cu (tu index 2 tro di, giu title=0 va divider=1)
            indexes_to_remove = list(range(lay.count() - 1, 1, -1))
            for idx in indexes_to_remove:
                item = lay.takeAt(idx)
                if item is None:
                    continue
                w = item.widget()
                if w:
                    w.setParent(None)
                    w.deleteLater()
                elif item.layout():
                    sub = item.layout()
                    while sub.count():
                        sub_item = sub.takeAt(0)
                        if sub_item.widget():
                            sub_item.widget().setParent(None)
                            sub_item.widget().deleteLater()

            from core.services.fine_service import get_overdue_list
            from core.utils.helpers import format_currency
            overdues = get_overdue_list()

            if not overdues:
                lbl = QLabel("Không có sách quá hạn")
                lbl.setStyleSheet(f"color: {styles.TEXT_MUTED}; border: none;")
                lay.addWidget(lbl)
            else:
                for od in overdues[:5]:
                    # Tao widget chua 1 dong
                    row_w = QWidget()
                    row_l = QHBoxLayout(row_w)
                    row_l.setContentsMargins(0, 4, 0, 4)
                    row_l.setSpacing(10)

                    name = od.get("Name", "")
                    av   = AvatarLabel(name[:2], styles.PRIMARY_LIGHT, styles.PRIMARY, 32, 8)

                    info_w = QWidget()
                    info_l = QVBoxLayout(info_w)
                    info_l.setContentsMargins(0, 0, 0, 0)
                    info_l.setSpacing(2)
                    ln = QLabel(name)
                    ln.setStyleSheet(f"color: {styles.TEXT_DARK}; font-weight: 600; border: none;")
                    lb = QLabel(f"{od.get('Title','')} — Quá {int(od.get('OverdueDays',0))} ngày")
                    lb.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
                    info_l.addWidget(ln)
                    info_l.addWidget(lb)

                    fl = QLabel(format_currency(od.get("FineAmount", 0)))
                    fl.setStyleSheet(f"color: {styles.DANGER}; font-weight: 600; border: none;")

                    row_l.addWidget(av)
                    row_l.addWidget(info_w)
                    row_l.addStretch()
                    row_l.addWidget(fl)

                    lay.addWidget(row_w)

        except Exception as e:
            print(f"[Dashboard] {e}")

class NavButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(styles.NAV_ITEM)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(42)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_active(self, active):
        self.setStyleSheet(styles.NAV_ACTIVE if active else styles.NAV_ITEM)


def sidebar_section(text):
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        "color: rgba(255,255,255,0.45); font-size: 11px; font-weight: 600;"
        "letter-spacing: 1px; padding: 12px 18px 4px 18px; border: none;"
    )
    return lbl


class DashboardWindow(QWidget):
    PAGE_TITLES = {
        "dashboard": "Dashboard",
        "books":     "Quản lý Sách",
        "students":  "Quản lý Độc giả",
        "borrow":    "Mượn / Trả Sách",
        "reports":   "Báo cáo & Thống kê",
        "staff":     "Quản lý Nhân viên",
    }

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 720)
        self.setMinimumSize(960, 640)
        self._nav_buttons = {}
        self._build_ui()
        self._center()
        try: update_overdue_status()
        except: pass
        self._show_page("dashboard")

    def _build_ui(self):
        root = QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # SIDEBAR
        sidebar = QWidget(); sidebar.setObjectName("Sidebar")
        sidebar.setStyleSheet(styles.SIDEBAR_BG); sidebar.setFixedWidth(220)
        sb = QVBoxLayout(sidebar); sb.setContentsMargins(0,0,0,0); sb.setSpacing(0)

        logo_area = QWidget()
        logo_area.setStyleSheet("border-bottom: 1px solid rgba(255,255,255,0.15);")
        li = QVBoxLayout(logo_area); li.setContentsMargins(18,20,18,16)
        lr = QHBoxLayout(); lr.setSpacing(10)
        logo_ic = AvatarLabel("LB", "rgba(255,255,255,0.2)", "white", 36, 10)
        lbl_app = QLabel(APP_NAME)
        lbl_app.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_app.setStyleSheet("color: white; border: none;")
        lbl_app.setWordWrap(True)
        lr.addWidget(logo_ic); lr.addWidget(lbl_app); lr.addStretch()
        li.addLayout(lr); sb.addWidget(logo_area)

        nav_area = QWidget()
        nl = QVBoxLayout(nav_area); nl.setContentsMargins(0,8,0,8); nl.setSpacing(0)
        pages = [
            ("Tổng quan", [("dashboard", "  Dashboard")]),
            ("Quản lý",   [
                ("books",    "  Quản lý Sách"),
                ("students", "  Độc giả"),
                ("borrow",   "  Mượn / Trả"),
            ]),
            ("Hệ thống",  [
                ("reports",  "  Báo cáo"),
                ("staff",    "  Nhân viên"),
            ]),
        ]
        for sec, items in pages:
            nl.addWidget(sidebar_section(sec))
            for key, label in items:
                btn = NavButton(label)
                btn.clicked.connect(lambda _, k=key: self._show_page(k))
                nl.addWidget(btn)
                self._nav_buttons[key] = btn
        nl.addStretch(); sb.addWidget(nav_area)

        footer = QWidget()
        footer.setStyleSheet("border-top: 1px solid rgba(255,255,255,0.15);")
        fl = QVBoxLayout(footer); fl.setContentsMargins(14,12,14,14); fl.setSpacing(8)
        name     = self.current_user.get("Name", "User")
        role     = self.current_user.get("Role", "staff")
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "AD"
        ur = QHBoxLayout(); ur.setSpacing(10)
        av = AvatarLabel(initials, "rgba(255,255,255,0.2)", "white", 34, 17)
        ui = QVBoxLayout(); ui.setSpacing(1)
        ln  = QLabel(name); ln.setStyleSheet("color: rgba(255,255,255,0.9); font-weight: 600; border: none;")
        lr2 = QLabel("Quản trị viên" if role == "admin" else "Nhân viên")
        lr2.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 12px; border: none;")
        ui.addWidget(ln); ui.addWidget(lr2)
        ur.addWidget(av); ur.addLayout(ui)
        fl.addLayout(ur)
        btn_lo = QPushButton("Đăng xuất")
        btn_lo.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.8);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px; padding: 8px 14px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.2); color: white; }
        """)
        btn_lo.setCursor(Qt.PointingHandCursor)
        btn_lo.setFixedHeight(36)
        btn_lo.clicked.connect(self._logout)
        fl.addWidget(btn_lo)
        sb.addWidget(footer)
        root.addWidget(sidebar)

        # MAIN
        main_area = QWidget(); main_area.setObjectName("Content")
        main_area.setStyleSheet(styles.CONTENT_BG)
        ml = QVBoxLayout(main_area); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)

        topbar = QWidget(); topbar.setObjectName("Topbar")
        topbar.setStyleSheet(styles.TOPBAR); topbar.setFixedHeight(56)
        tl = QHBoxLayout(topbar); tl.setContentsMargins(24,0,24,0)
        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.lbl_page_title.setStyleSheet(f"color: {styles.TEXT_DARK};")
        tl.addWidget(self.lbl_page_title); tl.addStretch()
        self.badge_overdue = QLabel()
        self.badge_overdue.setStyleSheet(
            f"background: {styles.DANGER}; color: white; border-radius: 12px;"
            f"font-weight: 600; padding: 4px 12px; font-size: 13px;"
        )
        self.badge_overdue.hide()
        tl.addWidget(self.badge_overdue)
        ml.addWidget(topbar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        from admin_app.gui.book_gui    import BookWindow
        from admin_app.gui.student_gui import StudentWindow
        from admin_app.gui.borrow_gui  import BorrowWindow
        from admin_app.gui.reports_gui import ReportsWindow
        from admin_app.gui.staff_gui   import StaffWindow

        self.screens = {
            "dashboard": DashboardScreen(),
            "books":     BookWindow(),
            "students":  StudentWindow(),
            "borrow":    BorrowWindow(),
            "reports":   ReportsWindow(),
            "staff":     StaffWindow(current_user=self.current_user),
        }
        for screen in self.screens.values():
            self.stack.addWidget(screen)
        ml.addWidget(self.stack)
        root.addWidget(main_area)

    def _show_page(self, key):
        self.stack.setCurrentWidget(self.screens[key])
        self.lbl_page_title.setText(self.PAGE_TITLES.get(key, key))
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)
        if key == "dashboard":
            self.screens["dashboard"].refresh()
            try:
                stats = get_dashboard_stats()
                od = stats.get("overdue", 0)
                if od > 0:
                    self.badge_overdue.setText(f"  {od} sách quá hạn  ")
                    self.badge_overdue.show()
                else:
                    self.badge_overdue.hide()
            except: pass
        if hasattr(self.screens.get(key), "refresh"):
            try: self.screens[key].refresh()
            except: pass

    def _logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất",
            "Bạn có chắc muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from admin_app.gui.login_gui import LoginWindow
            self.login = LoginWindow()
            self.login.show()
            self.close()

    def _center(self):
        from PyQt5.QtWidgets import QDesktopWidget
        geo = QDesktopWidget().screenGeometry()
        self.move(
            (geo.width()  - self.width())  // 2,
            (geo.height() - self.height()) // 2,
        )