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


def make_pill(text, bg, fg):
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setFixedHeight(22)
    lbl.setStyleSheet(
        f"background:{bg}; color:{fg}; border-radius:11px;"
        f"padding:0px 10px; font-size:12px; font-weight:600; border:none;")
    return lbl


class StatCard(QFrame):
    def __init__(self, title, value, icon, icon_bg, trend="", trend_color=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background:{styles.WHITE}; border:0.5px solid {styles.BORDER}; border-radius:12px; }}")
        self.setFixedHeight(100)
        lay = QHBoxLayout(self); lay.setContentsMargins(18,14,18,14); lay.setSpacing(14)

        ic = QLabel(icon); ic.setFixedSize(44,44); ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"background:{icon_bg}; border-radius:10px; border:none; font-size:20px;")
        lay.addWidget(ic)

        right = QVBoxLayout(); right.setSpacing(2)
        self.lbl_val = QLabel(str(value))
        self.lbl_val.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.lbl_val.setStyleSheet(f"color:{styles.TEXT_DARK}; border:none;")
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color:{styles.TEXT_MUTED}; font-size:12px; border:none;")
        right.addWidget(self.lbl_val); right.addWidget(self.lbl_title)
        if trend:
            tc = trend_color or styles.TEXT_MUTED
            self.lbl_trend = QLabel(trend)
            self.lbl_trend.setStyleSheet(f"color:{tc}; font-size:12px; border:none;")
            right.addWidget(self.lbl_trend)
        lay.addLayout(right); lay.addStretch()

    def set_value(self, v): self.lbl_val.setText(str(v))
    def set_trend(self, t, color=None):
        if hasattr(self, 'lbl_trend'):
            self.lbl_trend.setText(t)
            if color: self.lbl_trend.setStyleSheet(f"color:{color}; font-size:12px; border:none;")


class Panel(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background:{styles.WHITE}; border:0.5px solid {styles.BORDER}; border-radius:12px; }}")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(18,14,18,14); self._lay.setSpacing(8)
        if title:
            lbl = QLabel(title)
            lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
            lbl.setStyleSheet(f"color:{styles.TEXT_DARK}; border:none;")
            self._lay.addWidget(lbl)
            div = QFrame(); div.setFrameShape(QFrame.HLine)
            div.setStyleSheet(f"background:{styles.BORDER}; max-height:1px; border:none;")
            self._lay.addWidget(div)

    def layout(self): return self._lay


class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build()

    def _build(self):
        scroll = QScrollArea(self); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent; border:none;")
        container = QWidget()
        lay = QVBoxLayout(container); lay.setContentsMargins(24,20,24,20); lay.setSpacing(14)

        stats_row = QHBoxLayout(); stats_row.setSpacing(12)
        self.card_books    = StatCard("Tổng số sách", "...", "📚", "#E6F1FB", "Đang cập nhật...", styles.TEXT_MUTED)
        self.card_students = StatCard("Sinh viên",    "...", "👤", "#EAF3DE", "Đang cập nhật...", styles.TEXT_MUTED)
        self.card_borrow   = StatCard("Đang mượn",   "...", "📖", "#FAEEDA", "Đang cập nhật...", styles.TEXT_MUTED)
        self.card_overdue  = StatCard("Quá hạn/Mất", "...", "⚠",  "#FCEBEB", "Cần xử lý",       "#A32D2D")
        for c in [self.card_books, self.card_students, self.card_borrow, self.card_overdue]:
            stats_row.addWidget(c)
        lay.addLayout(stats_row)

        row2 = QHBoxLayout(); row2.setSpacing(12)
        self.panel_overdue = Panel("Sách quá hạn & mất sách")
        self.panel_overdue.setMinimumHeight(200)
        self.panel_chart   = Panel("Thống kê theo thể loại")
        self.panel_chart.setMinimumHeight(200)
        row2.addWidget(self.panel_overdue, 3)
        row2.addWidget(self.panel_chart, 2)
        lay.addLayout(row2)

        row3 = QHBoxLayout(); row3.setSpacing(12)
        self.panel_act = Panel("Hoạt động gần đây")
        self.panel_top = Panel("Top sách mượn nhiều")
        row3.addWidget(self.panel_act, 3)
        row3.addWidget(self.panel_top, 2)
        lay.addLayout(row3)

        lay.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

    def _clear_panel(self, panel, keep=2):
        lay = panel.layout()
        while lay.count() > keep:
            item = lay.takeAt(keep)
            if item is None:
                break
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
            elif item.layout() is not None:
                sub = item.layout()
                while sub.count():
                    c = sub.takeAt(0)
                    if c is not None:
                        cw = c.widget()
                        if cw is not None:
                            cw.setParent(None)
                            cw.deleteLater()

    def _make_divider(self):
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background:{styles.BORDER}; max-height:1px; border:none;")
        return div

    def refresh(self):
        try:
            stats = get_dashboard_stats()
            total_books = stats.get("total_books",0)
            total_sv    = stats.get("total_students",0)
            borrowing   = stats.get("borrowing",0)
            overdue     = stats.get("overdue",0)
            lost        = stats.get("lost",0)
            blocked     = stats.get("blocked",0)

            self.card_books.set_value(total_books)
            self.card_students.set_value(total_sv)
            self.card_students.set_trend(
                f"{blocked} thẻ bị khóa" if blocked > 0 else "Tất cả hợp lệ",
                "#A32D2D" if blocked > 0 else "#3B6D11")
            self.card_borrow.set_value(borrowing)
            self.card_overdue.set_value(overdue + lost)

            self._clear_panel(self.panel_overdue)
            lay = self.panel_overdue.layout()
            from core.services.fine_service import get_overdue_list
            overdues = get_overdue_list()
            def fmt(v): return f"{int(v):,}d".replace(",", ".") if v else "—"
            if not overdues:
                lbl = QLabel("Không có sách quá hạn hoặc mất")
                lbl.setStyleSheet(f"color:{styles.TEXT_MUTED}; border:none;")
                lay.addWidget(lbl)
            else:
                for od in overdues[:6]:
                    name    = od.get("Name","")
                    is_lost = od.get("Status","") == "Lost"
                    av_bg   = "#FCEBEB" if is_lost else "#FAEEDA"
                    av_fg   = "#A32D2D" if is_lost else "#633806"
                    days    = int(od.get("OverdueDays", 0))
                    sub_txt = (f"{od.get('Title','')} — Mất sách" if is_lost
                               else f"{od.get('Title','')} — Quá {days} ngày")

                    av = AvatarLabel(name[:2], av_bg, av_fg, 36, 8)

                    ln = QLabel(name)
                    ln.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:600; font-size:13px; border:none;")
                    lb = QLabel(sub_txt)
                    lb.setStyleSheet(f"color:{styles.TEXT_MUTED}; font-size:12px; border:none;")
                    lb.setWordWrap(True)

                    pill = make_pill(
                        "Mất sách" if is_lost else "Quá hạn",
                        "#FCEBEB" if is_lost else "#FAEEDA",
                        "#A32D2D" if is_lost else "#633806")

                    fl = QLabel(fmt(od.get("FineAmount", 0)))
                    fl.setStyleSheet(f"color:#A32D2D; font-weight:600; font-size:13px; border:none;")
                    fl.setFixedWidth(80)
                    fl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    row_w = QWidget()
                    row_w.setStyleSheet("background: transparent;")
                    row_l = QHBoxLayout(row_w)
                    row_l.setContentsMargins(4, 6, 4, 6)
                    row_l.setSpacing(10)

                    info_w = QWidget()
                    info_w.setStyleSheet("background: transparent;")
                    info_l = QVBoxLayout(info_w)
                    info_l.setContentsMargins(0, 0, 0, 0)
                    info_l.setSpacing(2)
                    info_l.addWidget(ln)
                    info_l.addWidget(lb)

                    row_l.addWidget(av)
                    row_l.addWidget(info_w, 1)
                    row_l.addWidget(pill)
                    row_l.addWidget(fl)
                    lay.addWidget(row_w)
                    if od != overdues[:6][-1]:
                        lay.addWidget(self._make_divider())

            self._clear_panel(self.panel_chart)
            lay2 = self.panel_chart.layout()
            from database.db import get_connection
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT bk.Category, COUNT(*) as cnt FROM Borrow b
                JOIN Books bk ON b.BookID=bk.BookID
                GROUP BY bk.Category ORDER BY cnt DESC LIMIT 6
            """)
            chart_rows = cur.fetchall(); conn.close()
            if not chart_rows:
                lay2.addWidget(QLabel("Chưa có dữ liệu"))
            else:
                max_cnt = max(r[1] for r in chart_rows) or 1
                for cat, cnt in chart_rows:
                    rw = QWidget()
                    rw.setStyleSheet("background: transparent;")
                    rl = QHBoxLayout(rw)
                    rl.setContentsMargins(0,2,0,2); rl.setSpacing(8)
                    lbl_cat = QLabel(cat or "Khác")
                    lbl_cat.setFixedWidth(90)
                    lbl_cat.setStyleSheet(f"color:{styles.TEXT_MID}; font-size:12px; border:none;")
                    track = QFrame(); track.setFixedHeight(8)
                    track.setStyleSheet(f"background:{styles.BG}; border-radius:4px; border:0.5px solid {styles.BORDER};")
                    fill = QFrame(track); fill.setFixedHeight(8)
                    fill.setStyleSheet(f"background:{styles.PRIMARY}; border-radius:4px; border:none;")
                    fill.setFixedWidth(max(6, int(cnt/max_cnt*100*1.6)))
                    lbl_cnt = QLabel(f"{cnt}")
                    lbl_cnt.setStyleSheet(f"color:{styles.TEXT_MID}; font-size:12px; border:none;")
                    lbl_cnt.setFixedWidth(20)
                    rl.addWidget(lbl_cat); rl.addWidget(track,1); rl.addWidget(lbl_cnt)
                    lay2.addWidget(rw)

            self._clear_panel(self.panel_act)
            lay3 = self.panel_act.layout()
            conn2 = get_connection(); cur2 = conn2.cursor()
            cur2.execute("""
                SELECT a.Action, a.TargetID, a.Timestamp, s.Name as StaffName,
                       a.Detail,
                       CASE
                           WHEN a.Action IN ('Mất sách','Giải quyết mất sách')
                           THEN (SELECT bk.Title FROM Borrow b
                                 JOIN Books bk ON b.BookID=bk.BookID
                                 WHERE b.BorrowID=CAST(a.TargetID AS INTEGER) LIMIT 1)
                           ELSE NULL
                       END as BookTitle
                FROM AuditLog a LEFT JOIN Staff s ON a.StaffID=s.StaffID
                ORDER BY a.LogID DESC LIMIT 8
            """)
            act_rows = cur2.fetchall(); conn2.close()

            DOT_COLORS = {
                "Thêm sách": "#3B6D11", "Sửa sách": "#185FA5",
                "Xoá sách": "#A32D2D", "Mất sách": "#A32D2D",
                "Giải quyết mất sách": "#3B6D11",
            }
            if not act_rows:
                lbl = QLabel("Chưa có hoạt động nào")
                lbl.setStyleSheet(f"color:{styles.TEXT_MUTED}; border:none;")
                lay3.addWidget(lbl)
            else:
                for row in act_rows:
                    action     = row["Action"] or ""
                    target     = row["TargetID"] or ""
                    ts         = row["Timestamp"] or ""
                    staff      = row["StaffName"] or "—"
                    book_title = row["BookTitle"] if row["BookTitle"] else None
                    try: ts_disp = ts[11:16]
                    except: ts_disp = ""
                    dot_color = DOT_COLORS.get(action, styles.PRIMARY)
                    if book_title:
                        target = book_title

                    rw = QWidget()
                    rw.setStyleSheet("background: transparent;")
                    rl = QHBoxLayout(rw)
                    rl.setContentsMargins(0,4,0,4); rl.setSpacing(10)

                    dot = QLabel("●"); dot.setFixedWidth(14)
                    dot.setStyleSheet(f"color:{dot_color}; font-size:10px; border:none;")

                    text_lbl = QLabel(f"{action} — {target}")
                    text_lbl.setStyleSheet(f"color:{styles.TEXT_DARK}; font-size:13px; border:none;")
                    sub_lbl = QLabel(staff)
                    sub_lbl.setStyleSheet(f"color:{styles.TEXT_MUTED}; font-size:12px; border:none;")

                    info_w = QWidget()
                    info_w.setStyleSheet("background: transparent;")
                    info_l = QVBoxLayout(info_w)
                    info_l.setContentsMargins(0,0,0,0); info_l.setSpacing(1)
                    info_l.addWidget(text_lbl); info_l.addWidget(sub_lbl)

                    time_lbl = QLabel(ts_disp)
                    time_lbl.setStyleSheet(f"color:{styles.TEXT_MUTED}; font-size:12px; border:none;")
                    time_lbl.setFixedWidth(40); time_lbl.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

                    rl.addWidget(dot); rl.addWidget(info_w,1); rl.addWidget(time_lbl)
                    lay3.addWidget(rw)
                    if row != act_rows[-1]:
                        lay3.addWidget(self._make_divider())

            self._clear_panel(self.panel_top)
            lay4 = self.panel_top.layout()
            conn3 = get_connection(); cur3 = conn3.cursor()
            cur3.execute("""
                SELECT bk.Title, COUNT(*) as cnt FROM Borrow b
                JOIN Books bk ON b.BookID=bk.BookID
                GROUP BY b.BookID ORDER BY cnt DESC LIMIT 5
            """)
            top_rows = cur3.fetchall(); conn3.close()
            RANK_BG = ["#E6F1FB","#E6F1FB","#EAF3DE","#EAF3DE","#EAF3DE"]
            RANK_FG = ["#0C447C","#0C447C","#27500A","#27500A","#27500A"]
            for idx, (title, cnt) in enumerate(top_rows):
                rw = QWidget()
                rw.setStyleSheet("background: transparent;")
                rl = QHBoxLayout(rw)
                rl.setContentsMargins(0,5,0,5); rl.setSpacing(10)
                rank = QLabel(str(idx+1)); rank.setFixedSize(28,28); rank.setAlignment(Qt.AlignCenter)
                rank.setStyleSheet(
                    f"background:{RANK_BG[idx]}; color:{RANK_FG[idx]};"
                    f"border-radius:6px; font-size:12px; font-weight:600; border:none;")
                t_lbl = QLabel(title)
                t_lbl.setStyleSheet(f"color:{styles.TEXT_DARK}; font-size:13px; border:none;")
                c_lbl = QLabel(f"{cnt} lần")
                c_lbl.setStyleSheet(f"color:{styles.TEXT_MUTED}; font-size:12px; border:none;")
                c_lbl.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
                rl.addWidget(rank); rl.addWidget(t_lbl,1); rl.addWidget(c_lbl)
                lay4.addWidget(rw)
                if idx < len(top_rows)-1:
                    lay4.addWidget(self._make_divider())

        except Exception as e:
            import traceback; traceback.print_exc()
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
        "color:rgba(255,255,255,0.45); font-size:11px; font-weight:600;"
        "letter-spacing:1px; padding:12px 18px 4px 18px; border:none;")
    return lbl


class DashboardWindow(QWidget):
    PAGE_TITLES = {
        "dashboard":     "Dashboard",
        "books":         "Quản lý Sach",
        "students":      "Quản lý Độc giả",
        "borrow":        "Mượn / Trả Sach",
        "reports":       "Báo cáo & Thong ke",
        "staff":         "Quản lý Nhân viên",
        "announcements": "Thông báo & Tiện ích",
        "messages":      "Tin nhắn",
    }

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 720); self.setMinimumSize(960, 640)
        self._nav_buttons = {}
        self._build_ui(); self._center()
        self._show_page("dashboard")

    def _build_ui(self):
        root = QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        sidebar = QWidget(); sidebar.setObjectName("Sidebar")
        sidebar.setStyleSheet(styles.SIDEBAR_BG); sidebar.setFixedWidth(220)
        sb = QVBoxLayout(sidebar); sb.setContentsMargins(0,0,0,0); sb.setSpacing(0)

        logo_area = QWidget()
        logo_area.setStyleSheet("border-bottom:1px solid rgba(255,255,255,0.15);")
        li = QVBoxLayout(logo_area); li.setContentsMargins(18,20,18,16)
        lr = QHBoxLayout(); lr.setSpacing(10)
        logo_ic = AvatarLabel("LB","rgba(255,255,255,0.2)","white",36,10)
        lbl_app = QLabel(APP_NAME)
        lbl_app.setFont(QFont("Segoe UI",11,QFont.Bold))
        lbl_app.setStyleSheet("color:white; border:none;"); lbl_app.setWordWrap(True)
        lr.addWidget(logo_ic); lr.addWidget(lbl_app); lr.addStretch()
        li.addLayout(lr); sb.addWidget(logo_area)

        nav_area = QWidget()
        nl = QVBoxLayout(nav_area); nl.setContentsMargins(0,8,0,8); nl.setSpacing(0)
        pages = [
            ("Tổng quan", [("dashboard","  Dashboard")]),
            ("Quản lý",   [("books","  Quản lý Sach"),("students","  Độc giả"),("borrow","  Mượn / Trả")]),
            ("Hệ thống",  [("reports","  Báo cáo"),("staff","  Nhân viên")]),
            ("Tiện ích",  [("announcements","  Thông báo & Tiện ích"),
                           ("messages","  Tin nhắn")]),
        ]
        for sec, items in pages:
            nl.addWidget(sidebar_section(sec))
            for key, label in items:
                btn = NavButton(label)
                btn.clicked.connect(lambda _, k=key: self._show_page(k))
                nl.addWidget(btn); self._nav_buttons[key] = btn
        nl.addStretch(); sb.addWidget(nav_area)

        footer = QWidget()
        footer.setStyleSheet("border-top:1px solid rgba(255,255,255,0.15);")
        fl = QVBoxLayout(footer); fl.setContentsMargins(14,12,14,14); fl.setSpacing(8)
        name     = self.current_user.get("Name","User")
        role     = self.current_user.get("Role","staff")
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "AD"
        ur = QHBoxLayout(); ur.setSpacing(10)
        av = AvatarLabel(initials,"rgba(255,255,255,0.2)","white",34,17)
        ui = QVBoxLayout(); ui.setSpacing(1)
        ln  = QLabel(name); ln.setStyleSheet("color:rgba(255,255,255,0.9); font-weight:600; border:none;")
        lr2 = QLabel("Quản trị viên" if role=="admin" else "Nhân viên")
        lr2.setStyleSheet("color:rgba(255,255,255,0.55); font-size:12px; border:none;")
        ui.addWidget(ln); ui.addWidget(lr2)
        ur.addWidget(av); ur.addLayout(ui)
        fl.addLayout(ur)
        btn_lo = QPushButton("Đăng xuất")
        btn_lo.setStyleSheet("""
            QPushButton { background:rgba(255,255,255,0.1); color:rgba(255,255,255,0.8);
                border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:8px 14px; }
            QPushButton:hover { background:rgba(255,255,255,0.2); color:white; }
        """)
        btn_lo.setCursor(Qt.PointingHandCursor); btn_lo.setFixedHeight(36)
        btn_lo.clicked.connect(self._logout)
        fl.addWidget(btn_lo); sb.addWidget(footer)
        root.addWidget(sidebar)

        main_area = QWidget(); main_area.setObjectName("Content")
        main_area.setStyleSheet(styles.CONTENT_BG)
        ml = QVBoxLayout(main_area); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)

        topbar = QWidget(); topbar.setObjectName("Topbar")
        topbar.setStyleSheet(styles.TOPBAR); topbar.setFixedHeight(56)
        tl = QHBoxLayout(topbar); tl.setContentsMargins(24,0,24,0)
        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setFont(QFont("Segoe UI",15,QFont.Bold))
        self.lbl_page_title.setStyleSheet(f"color:{styles.TEXT_DARK};")
        tl.addWidget(self.lbl_page_title); tl.addStretch()

        self.badge_lost = QLabel()
        self.badge_lost.setStyleSheet(
            "background:#FAEEDA; color:#633806; border-radius:12px;"
            "font-weight:600; padding:4px 12px; font-size:13px;")
        self.badge_lost.hide()
        self.badge_overdue = QLabel()
        self.badge_overdue.setStyleSheet(
            "background:#FCEBEB; color:#A32D2D; border-radius:12px;"
            "font-weight:600; padding:4px 12px; font-size:13px;")
        self.badge_overdue.hide()
        tl.addWidget(self.badge_lost); tl.addWidget(self.badge_overdue)
        ml.addWidget(topbar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")

        from admin_app.gui.book_gui         import BookWindow
        from admin_app.gui.student_gui      import StudentWindow
        from admin_app.gui.borrow_gui       import BorrowWindow
        from admin_app.gui.reports_gui      import ReportsWindow
        from admin_app.gui.staff_gui        import StaffWindow
        from admin_app.gui.announcement_gui import AnnouncementWindow
        from admin_app.gui.message_gui      import MessageWindow

        self.screens = {
            "dashboard":     DashboardScreen(),
            "books":         BookWindow(current_user=self.current_user),
            "students":      StudentWindow(),
            "borrow":        BorrowWindow(current_user=self.current_user),
            "reports":       ReportsWindow(),
            "staff":         StaffWindow(current_user=self.current_user),
            "announcements": AnnouncementWindow(current_user=self.current_user),
            "messages":      MessageWindow(current_user=self.current_user),
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
                od   = stats.get("overdue", 0)
                lost = stats.get("lost", 0)
                if lost > 0:
                    self.badge_lost.setText(f"  {lost} mất sách  ")
                    self.badge_lost.show()
                else:
                    self.badge_lost.hide()
                if od > 0:
                    self.badge_overdue.setText(f"  {od} quá hạn  ")
                    self.badge_overdue.show()
                else:
                    self.badge_overdue.hide()
            except: pass
        elif key == "borrow":
            try: self.screens["borrow"].refresh_table()
            except: pass
        elif key == "announcements":
            try: self.screens["announcements"].refresh()
            except: pass
        elif key == "messages":
            try: self.screens["messages"].refresh()
            except: pass
        elif key in ("books","students","reports","staff"):
            if hasattr(self.screens.get(key), "refresh"):
                try: self.screens[key].refresh()
                except: pass

    def _logout(self):
        msg = QMessageBox(self); msg.setWindowTitle("Đăng xuất")
        msg.setText("Bạn có chắc muốn đăng xuất?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Đăng xuất")
        msg.button(QMessageBox.No).setText("Huỷ")
        msg.setStyleSheet("""
            QMessageBox { background:#F7F8FC; }
            QLabel { color:#1E293B; font-size:14px; background:transparent; }
            QPushButton { background:white; color:#1E293B; border:1px solid #E2E8F0;
                border-radius:6px; padding:8px 24px; min-width:90px; }
            QPushButton:hover { background:#EBF1FD; color:#5B8DEF; }
        """)
        if msg.exec_() == QMessageBox.Yes:
            from shared.login_gui import LoginWindow
            self.login = LoginWindow(); self.login.show(); self.close()

    def _center(self):
        from PyQt5.QtWidgets import QDesktopWidget
        geo = QDesktopWidget().screenGeometry()
        self.move((geo.width()-self.width())//2, (geo.height()-self.height())//2)