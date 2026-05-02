# ── Student Portal GUI ─────────────────────────────────────────────────────
# Cổng thông tin sinh viên – PyQt5 Desktop App
# Các trang: HomePage, ExplorePage, BookDetailPage, StudentDashboard,
#            BorrowHistoryPage, BookRequestPage, ProfilePage, AnnouncementsPage
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QStackedWidget, QLineEdit, QScrollArea, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect, QRadioButton, QButtonGroup, QComboBox,
    QMessageBox, QDesktopWidget, QSpacerItem, QApplication,
    QDialog, QDateEdit, QTimeEdit, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit, QSpinBox, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal, QUrl, QDate, QTime
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QCursor, QLinearGradient, QDesktopServices

from core.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_BG,
    COLOR_PRIMARY_LIGHT, COLOR_WHITE, COLOR_TEXT_DARK,
    COLOR_TEXT_MID, COLOR_TEXT_MUTED, COLOR_BORDER,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, APP_NAME
)

# ── Hằng số màu sắc ──────────────────────────────────────────────────────────
NAV_BG = "#1E293B"
NAV_BG_DARK = "#0F172A"
GRADIENT_START = "#3B82F6"
GRADIENT_END = "#8B5CF6"

CATEGORY_COLORS = {
    "Lập trình":  {"bg": "#EEF2FF", "fg": "#4F46E5", "icon": "💻"},
    "CNTT":       {"bg": "#EEF2FF", "fg": "#4F46E5", "icon": "💻"},
    "Công nghệ thông tin": {"bg": "#EEF2FF", "fg": "#4F46E5", "icon": "💻"},
    "Ngoại ngữ":  {"bg": "#ECFDF5", "fg": "#059669", "icon": "🌐"},
    "Khoa học":   {"bg": "#FFFBEB", "fg": "#D97706", "icon": "🔬"},
    "Kinh tế":    {"bg": "#FFF1F2", "fg": "#E11D48", "icon": "📊"},
    "Toán học":   {"bg": "#F5F3FF", "fg": "#7C3AED", "icon": "📐"},
    "Tâm lý học": {"bg": "#FDF2F8", "fg": "#DB2777", "icon": "🧠"},
}
DEFAULT_CAT = {"bg": "#F1F5F9", "fg": "#64748B", "icon": "📚"}

FONT_FAMILY = "Segoe UI"


def _cat(category):
    """Trả về dict màu theo thể loại."""
    if not category:
        return DEFAULT_CAT
    for key, val in CATEGORY_COLORS.items():
        if key.lower() in category.lower():
            return val
    return DEFAULT_CAT


def _shadow(widget, blur=20, offset_y=4, alpha=40):
    """Thêm shadow nhẹ vào widget."""
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    eff.setOffset(0, offset_y)
    eff.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(eff)
    return widget


class ClickableFrame(QFrame):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.clicked.emit()


# ══════════════════════════════════════════════════════════════════════════════
#  AvatarLabel (dùng chung)
# ══════════════════════════════════════════════════════════════════════════════
class AvatarLabel(QWidget):
    def __init__(self, text="", bg="#8AAAE5", fg="white", size=34, radius=17, parent=None):
        super().__init__(parent)
        self._text = text[:2].upper() if text else ""
        self._bg = QColor(bg)
        self._fg = QColor(fg)
        self._r = radius
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._r, self._r)
        p.fillPath(path, self._bg)
        p.setPen(self._fg)
        p.setFont(QFont(FONT_FAMILY, 10, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, self._text)


# ══════════════════════════════════════════════════════════════════════════════
#  1. HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
class HomePage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _clear(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def refresh(self):
        self._clear()
        lay = self.main_layout

        # ── Hero Section ──────────────────────────────────────────────────
        hero = QWidget()
        hero.setMinimumHeight(280)
        hero.setObjectName("hero_bg")
        hero.setStyleSheet(f"""
            QWidget#hero_bg {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {GRADIENT_START}, stop:1 {GRADIENT_END}
                );
            }}
        """)

        hero_lay = QVBoxLayout(hero)
        hero_lay.setContentsMargins(40, 25, 40, 20)
        hero_lay.setSpacing(10)

        sub_top = QLabel("THƯ VIỆN ĐẠI HỌC CÔNG NGHỆ ĐÔNG Á")
        sub_top.setFont(QFont(FONT_FAMILY, 9, QFont.Bold))
        sub_top.setStyleSheet("color: rgba(255,255,255,0.7); background: transparent;")
        hero_lay.addWidget(sub_top)

        h1 = QLabel("Khám phá tri thức,\nnâng tầm nghiên cứu")
        h1.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        h1.setStyleSheet("color: white; background: transparent; padding-bottom: 15px;")
        hero_lay.addWidget(h1)

        hero_lay.addSpacing(10)

        # Ô tìm kiếm
        search_row = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm sách, giáo trình, tác giả...")
        self.inp_search.setFixedHeight(46)
        self.inp_search.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 0 18px;
                font-size: 14px;
                color: white;
            }}
            QLineEdit:focus {{
                background: white;
                color: #333;
            }}
        """)
        self.inp_search.returnPressed.connect(self._do_search)

        btn_search = QPushButton("Tìm kiếm")
        btn_search.setFixedSize(120, 46)
        btn_search.setCursor(Qt.PointingHandCursor)
        btn_search.setStyleSheet(f"""
            QPushButton {{
                background: #F5C05B;
                color: #2D3748;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #ECC94B; }}
        """)
        btn_search.clicked.connect(self._do_search)

        search_row.addWidget(self.inp_search, 1)
        search_row.addSpacing(10)
        search_row.addWidget(btn_search)
        hero_lay.addLayout(search_row)

        hero_lay.addStretch()
        lay.addWidget(hero)

        # ── Layout chính cho content ──────────────────────────────────────────
        content_lay = QVBoxLayout()
        content_lay.setContentsMargins(40, 30, 40, 40)
        content_lay.setSpacing(24)

        # ── 1. Sách mới nhập + Sách mượn nhiều (2 columns) ──────────────
        cols_lay = QHBoxLayout()
        cols_lay.setSpacing(20)

        # Trái: Sách mới nhập (dữ liệu thật)
        try:
            from core.services.book_service import get_new_books
            new_books = get_new_books(4)
        except:
            new_books = []

        tl_card = self._make_section_card("📗 Sách mới nhập kho")
        tl_vbox = QVBoxLayout()
        tl_vbox.setSpacing(0)

        if new_books:
            for book in new_books:
                frame = self._make_book_row(
                    book.get("Title", ""),
                    f"{book.get('Author', '')} • {book.get('Category', '')}",
                    "Mới", "#ECFDF5", "#059669", book
                )
                tl_vbox.addWidget(frame)
        else:
            lbl = QLabel("Chưa có sách trong kho")
            lbl.setStyleSheet("color: #718096; padding: 20px; border:none;")
            tl_vbox.addWidget(lbl)

        more_btn = QPushButton("Xem tất cả tài liệu →")
        more_btn.setStyleSheet("color: #D97706; font-size: 11px; text-align: left; border: none; padding: 10px 0;")
        more_btn.setCursor(Qt.PointingHandCursor)
        more_btn.clicked.connect(lambda: self.portal.show_page(1))
        tl_vbox.addWidget(more_btn)

        tl_card.layout().addLayout(tl_vbox)
        cols_lay.addWidget(tl_card, 1)

        # Phải: Sách mượn nhiều nhất (dữ liệu thật)
        try:
            from core.services.book_service import get_top_borrowed
            top_books = get_top_borrowed(4)
        except:
            top_books = []

        top_card = self._make_section_card("🔥 Sách mượn nhiều nhất")
        top_vbox = QVBoxLayout()
        top_vbox.setSpacing(0)

        if top_books:
            for i, book in enumerate(top_books):
                cnt = book.get("BorrowCount", 0)
                frame = self._make_book_row(
                    book.get("Title", ""),
                    f"{book.get('Author', '')} • {book.get('Category', '')}",
                    f"{cnt} lần", "#EEF2FF", "#4F46E5", book
                )
                top_vbox.addWidget(frame)
        else:
            lbl = QLabel("Chưa có dữ liệu mượn sách")
            lbl.setStyleSheet("color: #718096; padding: 20px; border:none;")
            top_vbox.addWidget(lbl)

        top_card.layout().addLayout(top_vbox)
        cols_lay.addWidget(top_card, 1)

        content_lay.addLayout(cols_lay)

        # ── 2. Thông báo (dữ liệu thật) ────────────────────────────────────
        try:
            from core.services.announcement_service import get_recent_announcements
            notices = get_recent_announcements(4)
        except:
            notices = []

        tb_card = self._make_section_card("")
        tb_header = QHBoxLayout()
        th = QLabel("🔔 Thông báo & Sự kiện")
        th.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        th.setStyleSheet("color: #1A2B4C; border:none;")
        tb_header.addWidget(th)
        tb_header.addStretch()

        more_th = QPushButton("Xem tất cả")
        more_th.setStyleSheet("color: #D97706; font-size: 11px; border:none;")
        more_th.setCursor(Qt.PointingHandCursor)
        more_th.clicked.connect(lambda: self.portal.show_page(6))
        tb_header.addWidget(more_th)
        tb_card.layout().addLayout(tb_header)

        tb_vbox = QVBoxLayout()
        tb_vbox.setSpacing(0)

        if notices:
            for n in notices:
                is_imp = n.get("IsImportant", 0)
                badge_t = "Quan trọng" if is_imp else "Mới"
                bg = "#FEF2F2" if is_imp else "#ECFDF5"
                fg = "#DC2626" if is_imp else "#059669"
                text = n.get("Title", "")
                content = n.get("Content", "")
                date_str = n.get("CreatedAt", "")[:10]

                row = QHBoxLayout()
                row.setContentsMargins(10, 12, 10, 12)

                badge = QLabel(badge_t)
                badge.setFixedSize(70, 24)
                badge.setAlignment(Qt.AlignCenter)
                badge.setStyleSheet(f"""
                    background: {bg}; color: {fg};
                    border-radius: 12px; font-size: 10px; font-weight: bold;
                """)
                row.addWidget(badge, alignment=Qt.AlignTop)
                row.addSpacing(12)

                vlay = QVBoxLayout()
                vlay.setSpacing(4)
                lbl = QLabel(text)
                lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
                lbl.setStyleSheet("color: #2D3748; border: none;")
                lbl.setWordWrap(True)
                vlay.addWidget(lbl)

                if content:
                    lbl_c = QLabel(content[:100])
                    lbl_c.setStyleSheet("color: #718096; font-size: 10px; border:none;")
                    lbl_c.setWordWrap(True)
                    vlay.addWidget(lbl_c)

                if date_str:
                    lbl_d = QLabel(date_str)
                    lbl_d.setStyleSheet("color: #A0AEC0; font-size: 10px; border:none;")
                    vlay.addWidget(lbl_d)

                row.addLayout(vlay)
                row.addStretch()

                frame = QFrame()
                frame.setObjectName("NoticeRow")
                frame.setStyleSheet("""
                    QFrame#NoticeRow { border-bottom: 1px solid #F1F5F9; border-radius: 8px; margin: 2px 10px; }
                    QFrame#NoticeRow:hover { background: #F8FAFC; border-bottom: 1px solid transparent; }
                """)
                frame.setLayout(row)
                tb_vbox.addWidget(frame)
        else:
            lbl = QLabel("Chưa có thông báo nào.")
            lbl.setStyleSheet("color: #718096; padding: 20px; border:none;")
            tb_vbox.addWidget(lbl)

        tb_card.layout().addLayout(tb_vbox)
        content_lay.addWidget(tb_card)

        content_lay.addStretch()
        lay.addLayout(content_lay)

    def _make_section_card(self, title):
        card = QFrame()
        card.setObjectName("SectionCard")
        card.setStyleSheet("""
            QFrame#SectionCard {
                background: white;
                border: 1px solid #F1F5F9;
                border-radius: 16px;
            }
        """)
        _shadow(card, blur=24, offset_y=6, alpha=25)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 10)
        lay.setSpacing(10)

        if title:
            title_lbl = QLabel(title)
            title_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
            title_lbl.setStyleSheet("color: #1A2B4C; border: none;")
            lay.addWidget(title_lbl)

        return card

    def _make_book_row(self, title, subtitle, badge_text, badge_bg, badge_fg, book_data=None):
        row = QHBoxLayout()
        row.setContentsMargins(12, 10, 12, 10)
        doc_lay = QVBoxLayout()
        doc_lay.setSpacing(4)
        lbl_main = QLabel(title)
        lbl_main.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        lbl_main.setStyleSheet("color: #2D3748; border: none;")

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("color: #718096; font-size: 11px; border: none;")

        doc_lay.addWidget(lbl_main)
        doc_lay.addWidget(lbl_sub)
        row.addLayout(doc_lay)

        lbl_badge = QLabel(badge_text)
        lbl_badge.setStyleSheet(f"""
            background: {badge_bg}; color: {badge_fg};
            border-radius: 12px; padding: 4px 10px;
            font-size: 10px; font-weight: bold; border: none;
        """)
        lbl_badge.setAlignment(Qt.AlignCenter)
        lbl_badge.setFixedHeight(24)
        row.addWidget(lbl_badge)

        frame = ClickableFrame()
        frame.setObjectName("BookRow")
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet("""
            QFrame#BookRow {
                background: transparent;
                border-bottom: 1px solid #F1F5F9;
                border-radius: 8px;
                margin: 2px 10px;
            }
            QFrame#BookRow:hover {
                background: #F8FAFC;
                border-bottom: 1px solid transparent;
            }
        """)
        frame.setLayout(row)
        if book_data:
            frame.clicked.connect(lambda _=False, b=book_data: self._open_book(b))
        return frame

    def _open_book(self, book):
        if hasattr(self.portal, 'book_detail_page'):
            self.portal.book_detail_page.load_book(book)
            self.portal.show_page(2)

    def _do_search(self):
        kw = self.inp_search.text().strip()
        if hasattr(self.portal, 'explore_page'):
            self.portal.explore_page.set_keyword(kw)
            self.portal.show_page(1)


# ══════════════════════════════════════════════════════════════════════════════
#  2. EXPLORE PAGE (Tra cứu tài liệu)
# ══════════════════════════════════════════════════════════════════════════════
class ExplorePage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self.active_filter = "Tất cả"
        self._build()

    def set_keyword(self, kw):
        self.inp_search.setText(kw)
        self._search()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC; border: none;")

        container = QWidget()
        container.setStyleSheet("background: #F8FAFC;")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Thanh tìm kiếm
        top_bar = QWidget()
        top_bar.setStyleSheet("background: #1A2B4C;")
        t_lay = QVBoxLayout(top_bar)
        t_lay.setContentsMargins(40, 20, 40, 20)

        search_row = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm kiếm sách, tác giả, ISBN...")
        self.inp_search.setFixedHeight(40)
        self.inp_search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px;
                padding: 0 16px;
                color: white;
            }
        """)
        self.inp_search.returnPressed.connect(self._search)

        btn_search = QPushButton("Tìm kiếm")
        btn_search.setFixedHeight(40)
        btn_search.setStyleSheet("""
            QPushButton {
                background: #F5C05B;
                color: #2D3748;
                border: none;
                border-radius: 6px;
                padding: 0 20px;
                font-weight: bold;
            }
        """)
        btn_search.clicked.connect(self._search)

        search_row.addWidget(self.inp_search, 1)
        search_row.addWidget(btn_search)
        t_lay.addLayout(search_row)

        # Filter nhanh
        filter_row = QHBoxLayout()
        filters = ["Tất cả", "Còn sẵn", "Hết sách"]
        self.filter_buttons = []
        for i, f in enumerate(filters):
            btn = QPushButton(f)
            btn.setCursor(Qt.PointingHandCursor)
            if i == 0:
                btn.setStyleSheet("background: #4A5568; color: #F5C05B; border-radius: 4px; padding: 4px 12px; border: none;")
            else:
                btn.setStyleSheet("background: transparent; color: rgba(255,255,255,0.8); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; padding: 4px 12px;")
            btn.clicked.connect(lambda _=False, txt=f, b=btn: self._on_filter_clicked(txt, b))
            self.filter_buttons.append(btn)
            filter_row.addWidget(btn)
        filter_row.addStretch()
        t_lay.addLayout(filter_row)

        lay.addWidget(top_bar)

        # ── Main Content ──────────────────────────────────────────────
        main_lay = QHBoxLayout()
        main_lay.setContentsMargins(40, 30, 40, 40)
        main_lay.setSpacing(30)

        # Left: Kết quả
        left_col = QVBoxLayout()
        self.lbl_count = QLabel("Hiển thị 0 kết quả")
        self.lbl_count.setStyleSheet("color: #718096; font-size: 13px; font-weight: bold; margin-bottom: 8px;")
        left_col.addWidget(self.lbl_count)

        self.list_container = QFrame()
        self.list_container.setObjectName("ExploreListContainer")
        self.list_container.setStyleSheet("QFrame#ExploreListContainer { background: white; border: 1px solid #F1F5F9; border-radius: 16px; }")
        _shadow(self.list_container, 24, 6, 25)

        self.v_list = QVBoxLayout(self.list_container)
        self.v_list.setContentsMargins(15, 10, 15, 10)
        self.v_list.setSpacing(0)
        self.v_list.setAlignment(Qt.AlignTop)

        left_col.addWidget(self.list_container)
        left_col.addStretch()
        main_lay.addLayout(left_col, 3)

        # Right: Lọc theo thể loại (dữ liệu thật)
        right_col = QVBoxLayout()
        filter_card = QFrame()
        filter_card.setObjectName("ExploreFilterCard")
        filter_card.setStyleSheet("QFrame#ExploreFilterCard { background: white; border: 1px solid #F1F5F9; border-radius: 16px; }")
        _shadow(filter_card, 24, 6, 25)
        fc_lay = QVBoxLayout(filter_card)
        fc_lay.setContentsMargins(24, 24, 24, 24)
        fc_lay.setSpacing(16)

        flbl = QLabel("Lọc theo thể loại")
        flbl.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
        flbl.setStyleSheet("border:none; color: #1A2B4C;")
        fc_lay.addWidget(flbl)

        self.cat_combo = QComboBox()
        self.cat_combo.addItem("Tất cả thể loại")
        try:
            from core.services.book_service import get_categories
            cats = get_categories()
            for c in cats:
                if c:
                    self.cat_combo.addItem(c)
        except:
            pass
        self.cat_combo.setItemDelegate(QStyledItemDelegate())
        self.cat_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 14px; border: 1px solid #E2E8F0; color: #1A2B4C;
                border-radius: 8px; font-size: 13px; background: white;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox:hover { border: 1px solid #CBD5E1; }
            QComboBox QAbstractItemView {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                background: white;
                selection-background-color: #EEF2FF;
                selection-color: #4F46E5;
                color: #2D3748;
                outline: 0px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 36px;
                padding-left: 10px;
                border: none;
            }
            QComboBox QAbstractItemView::item:hover {
                background: #F8FAFC;
                color: #4F46E5;
            }
        """)
        self.cat_combo.currentTextChanged.connect(lambda: self._search())
        fc_lay.addWidget(self.cat_combo)

        right_col.addWidget(filter_card)
        right_col.addStretch()
        main_lay.addLayout(right_col, 1)

        lay.addLayout(main_lay)
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _on_filter_clicked(self, txt, btn):
        self.active_filter = txt
        for b in self.filter_buttons:
            if b == btn:
                b.setStyleSheet("background: #4A5568; color: #F5C05B; border-radius: 4px; padding: 4px 12px; border: none;")
            else:
                b.setStyleSheet("background: transparent; color: rgba(255,255,255,0.8); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; padding: 4px 12px;")
        self._search()

    def _search(self):
        kw = self.inp_search.text().strip()
        cat = self.cat_combo.currentText()
        if cat == "Tất cả thể loại":
            cat = ""

        status = "all"
        if self.active_filter == "Còn sẵn":
            status = "available"

        try:
            from core.services.book_service import search_books
            books = search_books(kw, "", cat, status)

            if self.active_filter == "Hết sách":
                books = [b for b in books if b.get("Available", 0) <= 0]

            self._display_books(books)
        except Exception as e:
            print(f"[Explore] Search error: {e}")

    def _display_books(self, books):
        while self.v_list.count():
            item = self.v_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.lbl_count.setText(f"Hiển thị {len(books)} kết quả")

        if not books:
            no_data = QLabel("Không tìm thấy kết quả nào phù hợp.")
            no_data.setStyleSheet("color: #A0AEC0; font-size: 13px; padding: 40px; border: none;")
            no_data.setAlignment(Qt.AlignCenter)
            self.v_list.addWidget(no_data)
            return

        for book in books:
            card = self._make_list_item(book)
            self.v_list.addWidget(card)

    def _make_list_item(self, book):
        card = ClickableFrame()
        card.setObjectName("ExploreRowItem")
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
            QFrame#ExploreRowItem {
                background: transparent;
                border-bottom: 1px solid #F1F5F9;
                border-radius: 8px;
            }
            QFrame#ExploreRowItem:hover {
                background: #F8FAFC;
                border-bottom: 1px solid transparent;
            }
        """)
        card.setFixedHeight(100)

        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(16)

        # Cover
        cat_info = _cat(book.get("Category", ""))
        cover = QLabel(cat_info["icon"])
        cover.setFixedSize(50, 70)
        cover.setAlignment(Qt.AlignCenter)
        cover.setStyleSheet(f"background: {cat_info['bg']}; border-radius: 8px; font-size: 24px; border: none;")
        lay.addWidget(cover)

        # Info
        mid = QVBoxLayout()
        mid.setSpacing(6)
        title = QLabel(book.get("Title", ""))
        title.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        title.setStyleSheet("color: #1A2B4C; border: none;")
        mid.addWidget(title)

        author = QLabel(f"{book.get('Author', '')} • {book.get('Category', '')} • {book.get('Year', '')}")
        author.setStyleSheet("color: #718096; font-size: 12px; border: none;")
        mid.addWidget(author)

        avail = book.get("Available", 0)
        qty = book.get("Quantity", 0)
        avail_lbl = QLabel(f"Còn {avail}/{qty} cuốn")
        avail_color = "#059669" if avail > 0 else "#DC2626"
        avail_lbl.setStyleSheet(f"color: {avail_color}; font-size: 11px; border: none; font-weight: bold;")
        mid.addWidget(avail_lbl)

        lay.addLayout(mid, 1)

        # Buttons
        right = QVBoxLayout()
        right.setSpacing(6)

        b2 = QPushButton("Chi tiết")
        b2.setFixedSize(80, 32)
        b2.setCursor(Qt.PointingHandCursor)
        b2.setStyleSheet("""
            QPushButton { background: #EEF2FF; color: #4F46E5; border-radius: 8px; font-size: 12px; font-weight: bold; border: none; }
            QPushButton:hover { background: #4F46E5; color: white; }
        """)
        b2.clicked.connect(lambda _, b=book: self._open_book(b))

        right.addWidget(b2)
        right.addStretch()
        lay.addLayout(right)

        card.clicked.connect(lambda _=False, b=book: self._open_book(b))

        return card

    def _open_book(self, book):
        if hasattr(self.portal, 'book_detail_page'):
            self.portal.book_detail_page.load_book(book)
            self.portal.show_page(2)

    def refresh(self):
        self._search()


# ══════════════════════════════════════════════════════════════════════════════
#  3. BOOK DETAIL PAGE
# ══════════════════════════════════════════════════════════════════════════════
class BookDetailPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._current_book = None
        self._build()

    def _build(self):
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_lay = QVBoxLayout(self.container)
        self.main_lay.setContentsMargins(40, 30, 40, 30)
        self.main_lay.setSpacing(20)

        self.scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.scroll)

    def load_book(self, book):
        self._current_book = book
        self._clear()

        # Reload from DB
        try:
            from core.services.book_service import get_book_by_id
            fresh = get_book_by_id(book.get("BookID", ""))
            if fresh:
                book = fresh
                self._current_book = book
        except:
            pass

        cat_info = _cat(book.get("Category", ""))
        available = book.get("Available", 0)
        quantity = book.get("Quantity", 0)

        # ── Breadcrumb ────────────────────────────────────────────────────
        bread = QHBoxLayout()
        for text, action in [("🏠 Trang chủ", lambda: self.portal.show_page(0)),
                             (" > Khám phá", lambda: self.portal.show_page(1)),
                             (f" > {book.get('Title', '')[:40]}", None)]:
            lbl = QPushButton(text)
            lbl.setFlat(True)
            lbl.setCursor(Qt.PointingHandCursor if action else Qt.ArrowCursor)
            lbl.setStyleSheet(f"""
                QPushButton {{
                    color: {COLOR_PRIMARY if action else COLOR_TEXT_MUTED};
                    font-size: 12px; border: none; padding: 0; text-align: left;
                }}
                QPushButton:hover {{ text-decoration: underline; }}
            """)
            if action:
                lbl.clicked.connect(action)
            bread.addWidget(lbl)
        bread.addStretch()
        self.main_lay.addLayout(bread)

        # ── Main card ─────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: white; border: 1px solid {COLOR_BORDER}; border-radius: 16px; }}")
        _shadow(card, 20, 5, 30)

        card_lay = QHBoxLayout(card)
        card_lay.setContentsMargins(32, 32, 32, 32)
        card_lay.setSpacing(32)

        # Icon
        icon_container = QWidget()
        icon_container.setFixedSize(180, 180)
        icon_container.setStyleSheet(f"background: {cat_info['bg']}; border-radius: 20px;")
        ic_lay = QVBoxLayout(icon_container)
        ic_lay.setAlignment(Qt.AlignCenter)
        icon_lbl = QLabel(cat_info["icon"])
        icon_lbl.setFont(QFont(FONT_FAMILY, 50))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("border: none; background: transparent;")
        ic_lay.addWidget(icon_lbl)
        card_lay.addWidget(icon_container)

        # Info
        right = QVBoxLayout()
        right.setSpacing(10)

        # Badge row
        badge_row = QHBoxLayout()
        avail_badge = QLabel(f"  CÒN {available}/{quantity} SÁCH  ")
        avail_color = "#059669" if available > 0 else "#E11D48"
        avail_bg = "#ECFDF5" if available > 0 else "#FFF1F2"
        avail_badge.setStyleSheet(f"""
            background: {avail_bg}; color: {avail_color};
            border-radius: 10px; font-size: 11px; font-weight: bold;
            padding: 4px 12px; border: none;
        """)
        badge_row.addWidget(avail_badge)

        cat_badge = QLabel(f"  {book.get('Category', 'Khác')}  ")
        cat_badge.setStyleSheet(f"""
            background: {cat_info['bg']}; color: {cat_info['fg']};
            border-radius: 10px; font-size: 11px; font-weight: bold;
            padding: 4px 12px; border: none;
        """)
        badge_row.addWidget(cat_badge)
        badge_row.addStretch()
        right.addLayout(badge_row)

        # Title
        title = QLabel(book.get("Title", ""))
        title.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_DARK}; border: none;")
        title.setWordWrap(True)
        right.addWidget(title)

        author = QLabel(f"✍️ {book.get('Author', '')}")
        author.setFont(QFont(FONT_FAMILY, 11))
        author.setStyleSheet(f"color: {COLOR_TEXT_MID}; border: none;")
        right.addWidget(author)

        right.addSpacing(8)

        # Info grid
        info_grid = QGridLayout()
        info_grid.setSpacing(12)
        infos = [
            ("Nhà xuất bản", book.get("Publisher", "—")),
            ("Năm xuất bản", str(book.get("Year", "—"))),
            ("ISBN", book.get("ISBN", "—")),
            ("Vị trí kệ", book.get("Location", "—")),
        ]
        for idx, (label, value) in enumerate(infos):
            info_card = QFrame()
            info_card.setStyleSheet(f"QFrame {{ background: {COLOR_PRIMARY_BG}; border-radius: 8px; border: none; }}")
            il = QVBoxLayout(info_card)
            il.setContentsMargins(12, 8, 12, 8)
            il.setSpacing(2)
            il_label = QLabel(label)
            il_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; border: none;")
            il_value = QLabel(value)
            il_value.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
            il_value.setStyleSheet(f"color: {COLOR_TEXT_DARK}; border: none;")
            il.addWidget(il_label)
            il.addWidget(il_value)
            info_grid.addWidget(info_card, idx // 2, idx % 2)
        right.addLayout(info_grid)

        right.addSpacing(8)

        # ── Buttons: Mượn + Yêu thích ──────────────────────────────
        btn_row = QHBoxLayout()

        btn_borrow = QPushButton("📖 Đăng ký mượn sách")
        btn_borrow.setFixedHeight(42)
        btn_borrow.setCursor(Qt.PointingHandCursor)
        btn_borrow.setEnabled(available > 0)
        if available > 0:
            btn_borrow.setStyleSheet(f"""
                QPushButton {{ background: {NAV_BG}; color: white; border: none;
                    border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 20px; }}
                QPushButton:hover {{ background: {NAV_BG_DARK}; }}
            """)
        else:
            btn_borrow.setStyleSheet("QPushButton { background: #CBD5E0; color: white; border: none; border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 20px; }")
        btn_borrow.clicked.connect(self._borrow)
        btn_row.addWidget(btn_borrow)

        # Nút yêu thích
        is_fav = False
        try:
            from core.services.book_service import is_favorite
            sid = self.portal.current_student.get("StudentID", "")
            is_fav = is_favorite(sid, book.get("BookID", ""))
        except:
            pass

        fav_text = "💛 Đã yêu thích" if is_fav else "🤍 Yêu thích"
        btn_fav = QPushButton(fav_text)
        btn_fav.setFixedHeight(42)
        btn_fav.setCursor(Qt.PointingHandCursor)
        fav_bg = "#FEF3C7" if is_fav else "white"
        fav_fg = "#D97706" if is_fav else "#4A5568"
        btn_fav.setStyleSheet(f"""
            QPushButton {{ background: {fav_bg}; color: {fav_fg}; border: 1px solid #E2E8F0;
                border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 20px; }}
            QPushButton:hover {{ background: #FEF3C7; color: #D97706; }}
        """)
        btn_fav.clicked.connect(self._toggle_fav)
        btn_row.addWidget(btn_fav)

        btn_row.addStretch()
        right.addLayout(btn_row)

        right.addStretch()
        card_lay.addLayout(right, 1)
        self.main_lay.addWidget(card)

        # ── Reviews section ────────────────────────────────────────
        self._build_reviews_section(book)

        self.main_lay.addStretch()

    def _build_reviews_section(self, book):
        book_id = book.get("BookID", "")

        review_card = QFrame()
        review_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        rc_lay = QVBoxLayout(review_card)
        rc_lay.setContentsMargins(24, 20, 24, 20)
        rc_lay.setSpacing(12)

        # Header + avg rating
        try:
            from core.services.review_service import get_book_avg_rating, get_reviews_by_book
            avg, total = get_book_avg_rating(book_id)
            reviews = get_reviews_by_book(book_id)
        except:
            avg, total, reviews = 0, 0, []

        header_row = QHBoxLayout()
        h_lbl = QLabel(f"⭐ Đánh giá ({total} lượt)")
        h_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        h_lbl.setStyleSheet("color: #1A2B4C; border:none;")
        header_row.addWidget(h_lbl)

        if avg > 0:
            stars = "⭐" * int(round(avg))
            avg_lbl = QLabel(f" {avg}/5 {stars}")
            avg_lbl.setStyleSheet("color: #D97706; font-size: 13px; font-weight: bold; border:none;")
            header_row.addWidget(avg_lbl)

        header_row.addStretch()

        # Nút viết đánh giá
        btn_write = QPushButton("✏️ Viết đánh giá")
        btn_write.setCursor(Qt.PointingHandCursor)
        btn_write.setStyleSheet("""
            QPushButton { background: #F5C05B; color: #2D3748; border: none;
                border-radius: 6px; padding: 6px 16px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background: #ECC94B; }
        """)
        btn_write.clicked.connect(self._write_review)
        header_row.addWidget(btn_write)

        rc_lay.addLayout(header_row)

        # Danh sách đánh giá
        if reviews:
            for rv in reviews[:5]:
                rv_frame = QFrame()
                rv_frame.setStyleSheet("QFrame { border-bottom: 1px solid #F1F5F9; }")
                rv_lay = QVBoxLayout(rv_frame)
                rv_lay.setContentsMargins(0, 8, 0, 8)
                rv_lay.setSpacing(4)

                # Tên + sao
                name_row = QHBoxLayout()
                name_lbl = QLabel(f"👤 {rv.get('StudentName', 'Ẩn danh')}")
                name_lbl.setStyleSheet("color: #2D3748; font-weight: bold; font-size: 12px; border:none;")
                name_row.addWidget(name_lbl)

                rating = rv.get("Rating", 0)
                star_lbl = QLabel("⭐" * rating)
                star_lbl.setStyleSheet("font-size: 11px; border:none;")
                name_row.addWidget(star_lbl)

                date_lbl = QLabel(rv.get("CreatedAt", "")[:10])
                date_lbl.setStyleSheet("color: #A0AEC0; font-size: 10px; border:none;")
                name_row.addStretch()
                name_row.addWidget(date_lbl)
                rv_lay.addLayout(name_row)

                if rv.get("Comment"):
                    c_lbl = QLabel(rv["Comment"])
                    c_lbl.setWordWrap(True)
                    c_lbl.setStyleSheet("color: #4A5568; font-size: 11px; border:none; padding-left: 24px;")
                    rv_lay.addWidget(c_lbl)

                rc_lay.addWidget(rv_frame)
        else:
            no_lbl = QLabel("Chưa có đánh giá nào. Hãy là người đầu tiên!")
            no_lbl.setStyleSheet("color: #A0AEC0; font-size: 12px; padding: 10px; border:none;")
            rc_lay.addWidget(no_lbl)

        self.main_lay.addWidget(review_card)

    def _write_review(self):
        if not self._current_book:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Viết đánh giá")
        dlg.setFixedSize(400, 300)
        dlg.setStyleSheet("background: white;")

        fl = QFormLayout(dlg)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(12)

        spin = QSpinBox()
        spin.setRange(1, 5)
        spin.setValue(5)
        spin.setStyleSheet("padding: 6px; border: 1px solid #E2E8F0; border-radius: 6px;")
        fl.addRow("Số sao (1-5):", spin)

        txt = QTextEdit()
        txt.setPlaceholderText("Chia sẻ cảm nhận của bạn về cuốn sách...")
        txt.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px;")
        txt.setFixedHeight(120)
        fl.addRow("Nhận xét:", txt)

        btn = QPushButton("Gửi đánh giá")
        btn.setFixedHeight(38)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("background: #1A2B4C; color: white; border: none; border-radius: 8px; font-weight: bold;")

        def submit():
            try:
                from core.services.review_service import add_review
                sid = self.portal.current_student.get("StudentID", "")
                bid = self._current_book.get("BookID", "")
                ok, msg = add_review(sid, bid, spin.value(), txt.toPlainText().strip())
                if ok:
                    QMessageBox.information(dlg, "Thành công", msg)
                    dlg.accept()
                    self.load_book(self._current_book)
                else:
                    QMessageBox.warning(dlg, "Không thể đánh giá", msg)
            except Exception as e:
                QMessageBox.critical(dlg, "Lỗi", str(e))

        btn.clicked.connect(submit)
        fl.addRow(btn)
        dlg.exec_()

    def _borrow(self):
        if not self._current_book:
            return
        student = self.portal.current_student
        book_id = self._current_book.get("BookID", "")
        student_id = student.get("StudentID", "")

        try:
            from core.services.borrow_service import borrow_book
            ok, msg = borrow_book(student_id, book_id)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
                self.load_book(self._current_book)
            else:
                QMessageBox.warning(self, "Không thể mượn", msg)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _toggle_fav(self):
        if not self._current_book:
            return
        try:
            from core.services.book_service import toggle_favorite
            sid = self.portal.current_student.get("StudentID", "")
            bid = self._current_book.get("BookID", "")
            is_fav, msg = toggle_favorite(sid, bid)
            self.load_book(self._current_book)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _clear(self):
        while self.main_lay.count():
            item = self.main_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())


# ══════════════════════════════════════════════════════════════════════════════
#  4. STUDENT DASHBOARD (Trang cá nhân)
# ══════════════════════════════════════════════════════════════════════════════
class StudentDashboard(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build_shell()

    def _build_shell(self):
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.scroll)

    def _clear(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def refresh(self):
        self._clear()
        lay = self.main_layout

        student = self.portal.current_student
        name = student.get("Name", "Sinh viên")
        sid = student.get("StudentID", "")

        # Lấy stats thật
        try:
            from core.services.borrow_service import get_student_stats, get_student_borrows
            stats = get_student_stats(sid)
        except:
            stats = {"borrowing": 0, "overdue": 0, "total_fine": 0, "returned": 0, "due_soon": 0}

        # ── Header ────────────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background: #1A2B4C;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(40, 25, 40, 25)

        row = QHBoxLayout()
        v_left = QVBoxLayout()
        v_left.setSpacing(2)

        h1 = QLabel(f"Xin chào, <span style='font-style:italic; color:#F5C05B;'>{name}</span>")
        h1.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        h1.setStyleSheet("color: white;")
        v_left.addWidget(h1)

        card_status = student.get("CardStatus", "active")
        status_text = "🟢 Đang hoạt động" if card_status == "active" else "🔴 Bị khóa"
        lbl_info = QLabel(f"MSSV: {sid} • {status_text}")
        lbl_info.setStyleSheet("color: #94A3B8; font-size: 11px;")
        v_left.addWidget(lbl_info)

        row.addLayout(v_left)
        row.addStretch()
        h_lay.addLayout(row)
        lay.addWidget(header)

        # ── Stat Cards ────────────────────────────────────────────────────
        stats_ctn = QWidget()
        stats_ctn.setStyleSheet("background: #F8FAFC;")
        slay = QHBoxLayout(stats_ctn)
        slay.setContentsMargins(40, 25, 40, 10)
        slay.setSpacing(16)

        stat_items = [
            ("Đang mượn", str(stats.get("borrowing", 0)), "/ 3 tối đa", "#1A2B4C", "📖"),
            ("Sắp hết hạn", str(stats.get("due_soon", 0)), "trong 3 ngày", "#D97706", "⏰"),
            ("Quá hạn", str(stats.get("overdue", 0)), "cần trả ngay", "#DC2626", "⚠️"),
            ("Phí phạt", f"{stats.get('total_fine', 0):,.0f}đ", "chưa thanh toán", "#DC2626", "💰"),
            ("Đã trả", str(stats.get("returned", 0)), "cuốn", "#059669", "✅"),
        ]

        for title, val, sub, color, icon in stat_items:
            c = QFrame()
            c.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
            cl = QVBoxLayout(c)
            cl.setContentsMargins(16, 16, 16, 16)
            cl.setSpacing(6)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 18px; border:none;")
            cl.addWidget(icon_lbl)

            tl = QLabel(title)
            tl.setStyleSheet("color: #718096; font-size: 10px; border:none;")
            cl.addWidget(tl)

            val_l = QLabel(val)
            val_l.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
            val_l.setStyleSheet(f"color: {color}; border:none;")
            cl.addWidget(val_l)

            sub_l = QLabel(sub)
            sub_l.setStyleSheet("color: #A0AEC0; font-size: 10px; border:none;")
            cl.addWidget(sub_l)
            slay.addWidget(c)

        lay.addWidget(stats_ctn)

        # ── 2 Columns ────────────────────────────────────────────────────
        main_area = QHBoxLayout()
        main_area.setContentsMargins(40, 20, 40, 40)
        main_area.setSpacing(24)

        # Left: Sách đang mượn (dữ liệu thật)
        left = QVBoxLayout()

        sach = QFrame()
        sach.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        sach_lay = QVBoxLayout(sach)
        sach_lay.setContentsMargins(20, 20, 20, 20)
        sach_lay.setSpacing(0)

        lt = QLabel("📚 Sách đang mượn")
        lt.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        lt.setStyleSheet("color: #1A2B4C; border:none;")
        sach_lay.addWidget(lt)
        sach_lay.addSpacing(15)

        try:
            from core.services.borrow_service import get_student_borrows
            borrows = get_student_borrows(sid, "active")
        except:
            borrows = []

        if borrows:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            for br in borrows:
                r = QHBoxLayout()
                r.setContentsMargins(0, 10, 0, 10)

                vl = QVBoxLayout()
                vl.setSpacing(2)
                tt = QLabel(br.get("BookTitle", ""))
                tt.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
                tt.setStyleSheet("color: #2D3748; border:none;")
                vl.addWidget(tt)

                due = br.get("DueDate", "")
                status = br.get("Status", "")
                renew = br.get("RenewCount", 0) or 0
                renew_txt = " (đã gia hạn)" if renew > 0 else ""

                sl = QLabel(f"Hạn trả: {due}{renew_txt}")
                if status == "Overdue":
                    sl.setStyleSheet("color: #DC2626; font-size: 10px; border:none; font-weight: bold;")
                else:
                    sl.setStyleSheet("color: #718096; font-size: 10px; border:none;")
                vl.addWidget(sl)
                r.addLayout(vl)
                r.addStretch()

                # Badge trạng thái
                if status == "Overdue":
                    badge_text, bbg, bfg = "Quá hạn", "#FEF2F2", "#DC2626"
                elif due <= today:
                    badge_text, bbg, bfg = "Hôm nay", "#FEF3C7", "#D97706"
                else:
                    from datetime import datetime as dt
                    days_left = (dt.strptime(due, "%Y-%m-%d") - dt.strptime(today, "%Y-%m-%d")).days
                    badge_text = f"{days_left} ngày"
                    if days_left <= 3:
                        bbg, bfg = "#FEF3C7", "#D97706"
                    else:
                        bbg, bfg = "#ECFDF5", "#059669"

                bl = QLabel(badge_text)
                bl.setFixedSize(65, 24)
                bl.setAlignment(Qt.AlignCenter)
                bl.setStyleSheet(f"background: {bbg}; color: {bfg}; font-size: 10px; border-radius: 12px; font-weight:bold; border:none;")
                r.addWidget(bl)

                # Nút gia hạn
                if status == "Borrowing" and renew < 1:
                    btn_renew = QPushButton("Gia hạn")
                    btn_renew.setFixedSize(65, 24)
                    btn_renew.setCursor(Qt.PointingHandCursor)
                    btn_renew.setStyleSheet("""
                        QPushButton { background: #EEF2FF; color: #4F46E5; border: none;
                            border-radius: 12px; font-size: 10px; font-weight: bold; }
                        QPushButton:hover { background: #4F46E5; color: white; }
                    """)
                    borrow_id = br.get("BorrowID")
                    btn_renew.clicked.connect(lambda _=False, bid=borrow_id: self._renew(bid))
                    r.addWidget(btn_renew)

                fr = QFrame()
                fr.setStyleSheet("border-bottom: 1px solid #E2E8F0;")
                fr.setLayout(r)
                sach_lay.addWidget(fr)
        else:
            no_lbl = QLabel("Bạn chưa mượn cuốn sách nào.")
            no_lbl.setStyleSheet("color: #A0AEC0; font-size: 12px; padding: 20px; border:none;")
            sach_lay.addWidget(no_lbl)

        sach_lay.addSpacing(15)

        acts = QHBoxLayout()
        ls = QPushButton("Xem lịch sử mượn trả →")
        ls.setCursor(Qt.PointingHandCursor)
        ls.setStyleSheet("background: transparent; color: #D97706; font-size: 11px; border:none; font-weight: bold;")
        ls.clicked.connect(lambda: self.portal.show_page(4))
        acts.addWidget(ls)
        acts.addStretch()
        sach_lay.addLayout(acts)

        left.addWidget(sach)
        left.addStretch()
        main_area.addLayout(left, 6)

        # Right: Gợi ý sách (dữ liệu thật)
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        gy = QFrame()
        gy.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        gl = QVBoxLayout(gy)
        gl.setContentsMargins(20, 20, 20, 20)
        gl.setSpacing(0)

        glt = QLabel("💡 Gợi ý cho bạn")
        glt.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        glt.setStyleSheet("color: #1A2B4C; border:none;")
        gl.addWidget(glt)
        gl.addSpacing(12)

        try:
            from core.services.book_service import get_recommended_books
            recs = get_recommended_books(sid, 4)
        except:
            recs = []

        if recs:
            for book in recs:
                r = QHBoxLayout()
                r.setContentsMargins(0, 8, 0, 8)
                vl = QVBoxLayout()
                vl.setSpacing(2)
                l1 = QLabel(book.get("Title", ""))
                l1.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
                l1.setStyleSheet("color: #2D3748; border:none;")
                vl.addWidget(l1)
                l2 = QLabel(f"{book.get('Author', '')} • {book.get('Category', '')}")
                l2.setStyleSheet("color: #718096; font-size: 10px; border:none;")
                vl.addWidget(l2)
                r.addLayout(vl)
                r.addStretch()

                fr = ClickableFrame()
                fr.setStyleSheet("QFrame { border-bottom: 1px solid #E2E8F0; } QFrame:hover { background: #F8FAFC; }")
                fr.setCursor(Qt.PointingHandCursor)
                fr.setLayout(r)
                fr.clicked.connect(lambda _=False, b=book: self._open_book(b))
                gl.addWidget(fr)
        else:
            no_lbl = QLabel("Chưa có gợi ý. Hãy mượn sách để nhận gợi ý!")
            no_lbl.setStyleSheet("color: #A0AEC0; font-size: 11px; border:none; padding: 10px;")
            no_lbl.setWordWrap(True)
            gl.addWidget(no_lbl)

        right_col.addWidget(gy)

        # ── Sách yêu thích ──
        fav = QFrame()
        fav.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        fl = QVBoxLayout(fav)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(0)

        flt = QLabel("❤️ Sách yêu thích")
        flt.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        flt.setStyleSheet("color: #1A2B4C; border:none;")
        fl.addWidget(flt)
        fl.addSpacing(12)

        try:
            from core.services.book_service import get_favorites
            fav_books = get_favorites(sid)
        except:
            fav_books = []

        if fav_books:
            for book in fav_books[:4]:
                rf = QHBoxLayout()
                rf.setContentsMargins(0, 8, 0, 8)
                vlf = QVBoxLayout()
                vlf.setSpacing(2)
                l1f = QLabel(book.get("Title", ""))
                l1f.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
                l1f.setStyleSheet("color: #2D3748; border:none;")
                vlf.addWidget(l1f)
                l2f = QLabel(f"{book.get('Author', '')} • {book.get('Category', '')}")
                l2f.setStyleSheet("color: #718096; font-size: 10px; border:none;")
                vlf.addWidget(l2f)
                rf.addLayout(vlf)
                rf.addStretch()

                frf = ClickableFrame()
                frf.setStyleSheet("QFrame { border-bottom: 1px solid #E2E8F0; } QFrame:hover { background: #F8FAFC; }")
                frf.setCursor(Qt.PointingHandCursor)
                frf.setLayout(rf)
                frf.clicked.connect(lambda _=False, b=book: self._open_book(b))
                fl.addWidget(frf)
                
            if len(fav_books) > 4:
                more_lbl = QLabel(f"và {len(fav_books)-4} sách khác...")
                more_lbl.setStyleSheet("color: #A0AEC0; font-size: 11px; font-style: italic; border:none; padding: 10px 0 0 0;")
                fl.addWidget(more_lbl)
        else:
            nof_lbl = QLabel("Bạn chưa đánh dấu yêu thích cuốn nào.")
            nof_lbl.setStyleSheet("color: #A0AEC0; font-size: 11px; border:none; padding: 10px;")
            nof_lbl.setWordWrap(True)
            fl.addWidget(nof_lbl)

        right_col.addWidget(fav)

        right_col.addStretch()
        main_area.addLayout(right_col, 4)

        lay.addLayout(main_area)

    def _renew(self, borrow_id):
        try:
            from core.services.borrow_service import renew_book
            sid = self.portal.current_student.get("StudentID", "")
            ok, msg = renew_book(borrow_id, sid)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
            else:
                QMessageBox.warning(self, "Không thể gia hạn", msg)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _open_book(self, book):
        if hasattr(self.portal, 'book_detail_page'):
            self.portal.book_detail_page.load_book(book)
            self.portal.show_page(2)


# ══════════════════════════════════════════════════════════════════════════════
#  5. BORROW HISTORY PAGE (Lịch sử mượn trả)
# ══════════════════════════════════════════════════════════════════════════════
class BorrowHistoryPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self.filter = "all"
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _clear(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def _cl(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def refresh(self):
        self._clear()
        lay = self.main_layout

        # Header
        header = QWidget()
        header.setStyleSheet("background: #1A2B4C;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(40, 25, 40, 25)

        h1 = QLabel("📋 Lịch sử mượn trả")
        h1.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        h1.setStyleSheet("color: white;")
        h_lay.addWidget(h1)

        # Filter buttons
        f_row = QHBoxLayout()
        self.hist_filter_btns = []
        for txt in ["Tất cả", "Đang mượn", "Đã trả", "Quá hạn"]:
            btn = QPushButton(txt)
            btn.setCursor(Qt.PointingHandCursor)
            active = (txt == "Tất cả" and self.filter == "all") or \
                     (txt == "Đang mượn" and self.filter == "active") or \
                     (txt == "Đã trả" and self.filter == "returned") or \
                     (txt == "Quá hạn" and self.filter == "overdue")
            if active:
                btn.setStyleSheet("background: #4A5568; color: #F5C05B; border-radius: 4px; padding: 4px 12px; border: none;")
            else:
                btn.setStyleSheet("background: transparent; color: rgba(255,255,255,0.8); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; padding: 4px 12px;")

            filter_map = {"Tất cả": "all", "Đang mượn": "active", "Đã trả": "returned", "Quá hạn": "overdue"}
            btn.clicked.connect(lambda _=False, f=filter_map.get(txt, "all"): self._set_filter(f))
            self.hist_filter_btns.append(btn)
            f_row.addWidget(btn)
        f_row.addStretch()
        h_lay.addLayout(f_row)
        lay.addWidget(header)

        # Table
        content = QVBoxLayout()
        content.setContentsMargins(40, 25, 40, 40)
        content.setSpacing(12)

        sid = self.portal.current_student.get("StudentID", "")
        try:
            from core.services.borrow_service import get_student_borrows
            borrows = get_student_borrows(sid, self.filter)
        except:
            borrows = []

        lbl_count = QLabel(f"Tổng cộng: {len(borrows)} phiếu mượn")
        lbl_count.setStyleSheet("color: #718096; font-size: 11px;")
        content.addWidget(lbl_count)

        for br in borrows:
            card = QFrame()
            card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 10px; }")

            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 16, 20, 16)
            cl.setSpacing(16)

            # Book icon
            cat_info = _cat(br.get("Category", ""))
            ic = QLabel(cat_info["icon"])
            ic.setFixedSize(40, 40)
            ic.setAlignment(Qt.AlignCenter)
            ic.setStyleSheet(f"background: {cat_info['bg']}; border-radius: 8px; font-size: 18px;")
            cl.addWidget(ic)

            # Info
            info = QVBoxLayout()
            info.setSpacing(3)
            t_lbl = QLabel(br.get("BookTitle", ""))
            t_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
            t_lbl.setStyleSheet("color: #1A2B4C; border:none;")
            info.addWidget(t_lbl)

            renew_count = br.get("RenewCount", 0) or 0
            renew_txt = f" • Đã gia hạn {renew_count} lần" if renew_count > 0 else ""
            d_lbl = QLabel(f"Mượn: {br.get('BorrowDate', '')} → Hạn: {br.get('DueDate', '')}{renew_txt}")
            d_lbl.setStyleSheet("color: #718096; font-size: 10px; border:none;")
            info.addWidget(d_lbl)

            if br.get("ReturnDate"):
                r_lbl = QLabel(f"Trả ngày: {br['ReturnDate']}")
                r_lbl.setStyleSheet("color: #059669; font-size: 10px; border:none;")
                info.addWidget(r_lbl)

            fine = br.get("FineAmount", 0) or 0
            if fine > 0:
                f_lbl = QLabel(f"Phí phạt: {fine:,.0f}đ")
                f_lbl.setStyleSheet("color: #DC2626; font-size: 10px; font-weight: bold; border:none;")
                info.addWidget(f_lbl)

            cl.addLayout(info, 1)

            # Status badge
            status = br.get("Status", "")
            status_map = {
                "Borrowing": ("Đang mượn", "#EEF2FF", "#4F46E5"),
                "Returned": ("Đã trả", "#ECFDF5", "#059669"),
                "Overdue": ("Quá hạn", "#FEF2F2", "#DC2626"),
                "Lost": ("Mất sách", "#FEF2F2", "#DC2626"),
            }
            s_text, s_bg, s_fg = status_map.get(status, ("—", "#F1F5F9", "#64748B"))
            s_lbl = QLabel(s_text)
            s_lbl.setFixedSize(75, 26)
            s_lbl.setAlignment(Qt.AlignCenter)
            s_lbl.setStyleSheet(f"background: {s_bg}; color: {s_fg}; border-radius: 13px; font-size: 11px; font-weight: bold;")
            cl.addWidget(s_lbl)

            # Renew button
            if status == "Borrowing" and renew_count < 1:
                btn_renew = QPushButton("Gia hạn")
                btn_renew.setFixedSize(70, 28)
                btn_renew.setCursor(Qt.PointingHandCursor)
                btn_renew.setStyleSheet("""
                    QPushButton { background: #EEF2FF; color: #4F46E5; border: none;
                        border-radius: 14px; font-size: 11px; font-weight: bold; }
                    QPushButton:hover { background: #4F46E5; color: white; }
                """)
                bid = br.get("BorrowID")
                btn_renew.clicked.connect(lambda _=False, b=bid: self._renew(b))
                cl.addWidget(btn_renew)

            content.addWidget(card)

        if not borrows:
            no_lbl = QLabel("Chưa có lịch sử mượn trả.")
            no_lbl.setStyleSheet("color: #A0AEC0; font-size: 13px; padding: 30px;")
            no_lbl.setAlignment(Qt.AlignCenter)
            content.addWidget(no_lbl)

        content.addStretch()
        lay.addLayout(content)

    def _set_filter(self, f):
        self.filter = f
        self.refresh()

    def _renew(self, borrow_id):
        try:
            from core.services.borrow_service import renew_book
            sid = self.portal.current_student.get("StudentID", "")
            ok, msg = renew_book(borrow_id, sid)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
            else:
                QMessageBox.warning(self, "Không thể gia hạn", msg)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  6. BOOK REQUEST PAGE (Đề xuất mua sách)
# ══════════════════════════════════════════════════════════════════════════════
class BookRequestPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _clear(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def _cl(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def refresh(self):
        self._clear()
        lay = self.main_layout

        # Header
        header = QWidget()
        header.setStyleSheet("background: #1A2B4C;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(40, 25, 40, 25)

        h1 = QLabel("📝 Đề xuất mua sách mới")
        h1.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        h1.setStyleSheet("color: white;")
        h_lay.addWidget(h1)

        sub = QLabel("Bạn muốn thư viện nhập sách gì? Hãy gửi đề xuất!")
        sub.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        h_lay.addWidget(sub)
        lay.addWidget(header)

        content = QVBoxLayout()
        content.setContentsMargins(40, 25, 40, 40)
        content.setSpacing(20)

        # ── Form đề xuất ──────────────────────────────────────
        form_card = QFrame()
        form_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        fc_lay = QVBoxLayout(form_card)
        fc_lay.setContentsMargins(24, 24, 24, 24)
        fc_lay.setSpacing(14)

        fc_title = QLabel("Gửi đề xuất mới")
        fc_title.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        fc_title.setStyleSheet("color: #1A2B4C; border:none;")
        fc_lay.addWidget(fc_title)

        fl = QFormLayout()
        fl.setSpacing(10)

        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nhập tên sách bạn muốn thư viện nhập...")
        self.inp_title.setFixedHeight(38)
        self.inp_title.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 6px; padding: 0 12px;")
        fl.addRow("Tên sách *:", self.inp_title)

        self.inp_author = QLineEdit()
        self.inp_author.setPlaceholderText("Tác giả (nếu biết)")
        self.inp_author.setFixedHeight(38)
        self.inp_author.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 6px; padding: 0 12px;")
        fl.addRow("Tác giả:", self.inp_author)

        self.inp_reason = QTextEdit()
        self.inp_reason.setPlaceholderText("Lý do bạn muốn thư viện nhập sách này...")
        self.inp_reason.setFixedHeight(80)
        self.inp_reason.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px;")
        fl.addRow("Lý do:", self.inp_reason)

        fc_lay.addLayout(fl)

        btn_submit = QPushButton("📤 Gửi đề xuất")
        btn_submit.setFixedHeight(40)
        btn_submit.setCursor(Qt.PointingHandCursor)
        btn_submit.setStyleSheet("""
            QPushButton { background: #1A2B4C; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background: #0F172A; }
        """)
        btn_submit.clicked.connect(self._submit_request)
        fc_lay.addWidget(btn_submit)
        content.addWidget(form_card)

        # ── Danh sách đề xuất của tôi ──────────────────────────────
        list_card = QFrame()
        list_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        lc_lay = QVBoxLayout(list_card)
        lc_lay.setContentsMargins(24, 20, 24, 20)
        lc_lay.setSpacing(10)

        lc_title = QLabel("📋 Đề xuất của tôi")
        lc_title.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        lc_title.setStyleSheet("color: #1A2B4C; border:none;")
        lc_lay.addWidget(lc_title)

        sid = self.portal.current_student.get("StudentID", "")
        try:
            from core.services.book_request_service import get_requests_by_student
            requests = get_requests_by_student(sid)
        except:
            requests = []

        if requests:
            for req in requests:
                r_frame = QFrame()
                r_frame.setStyleSheet("QFrame { border-bottom: 1px solid #F1F5F9; }")
                r_lay = QHBoxLayout(r_frame)
                r_lay.setContentsMargins(0, 10, 0, 10)
                r_lay.setSpacing(12)

                info = QVBoxLayout()
                info.setSpacing(3)
                t_lbl = QLabel(req.get("BookTitle", ""))
                t_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
                t_lbl.setStyleSheet("color: #2D3748; border:none;")
                info.addWidget(t_lbl)

                a_lbl = QLabel(f"Tác giả: {req.get('Author', '—')} • {req.get('CreatedAt', '')[:10]}")
                a_lbl.setStyleSheet("color: #718096; font-size: 10px; border:none;")
                info.addWidget(a_lbl)

                note = req.get("AdminNote", "")
                if note:
                    n_lbl = QLabel(f"💬 {note}")
                    n_lbl.setStyleSheet("color: #4F46E5; font-size: 10px; border:none;")
                    info.addWidget(n_lbl)

                r_lay.addLayout(info, 1)

                # Status badge
                st = req.get("Status", "Pending")
                st_map = {
                    "Pending": ("Chờ duyệt", "#FEF3C7", "#D97706"),
                    "Approved": ("Đã duyệt", "#ECFDF5", "#059669"),
                    "Rejected": ("Từ chối", "#FEF2F2", "#DC2626"),
                }
                s_text, s_bg, s_fg = st_map.get(st, ("—", "#F1F5F9", "#64748B"))
                s_lbl = QLabel(s_text)
                s_lbl.setFixedSize(75, 24)
                s_lbl.setAlignment(Qt.AlignCenter)
                s_lbl.setStyleSheet(f"background: {s_bg}; color: {s_fg}; border-radius: 12px; font-size: 10px; font-weight: bold;")
                r_lay.addWidget(s_lbl)

                lc_lay.addWidget(r_frame)
        else:
            no_lbl = QLabel("Bạn chưa gửi đề xuất nào.")
            no_lbl.setStyleSheet("color: #A0AEC0; font-size: 12px; padding: 15px; border:none;")
            lc_lay.addWidget(no_lbl)

        content.addWidget(list_card)
        content.addStretch()
        lay.addLayout(content)

    def _submit_request(self):
        title = self.inp_title.text().strip()
        author = self.inp_author.text().strip()
        reason = self.inp_reason.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên sách.")
            return

        try:
            from core.services.book_request_service import add_request
            sid = self.portal.current_student.get("StudentID", "")
            ok, msg = add_request(sid, title, author, reason)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Lỗi", msg)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  7. ANNOUNCEMENTS PAGE (Thông báo)
# ══════════════════════════════════════════════════════════════════════════════
class AnnouncementsPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _clear(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def _cl(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def refresh(self):
        self._clear()
        lay = self.main_layout

        # Header
        header = QWidget()
        header.setStyleSheet("background: #1A2B4C;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(40, 25, 40, 25)

        h1 = QLabel("🔔 Thông báo & Sự kiện")
        h1.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        h1.setStyleSheet("color: white;")
        h_lay.addWidget(h1)

        sub = QLabel("Các thông báo mới nhất từ thư viện")
        sub.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        h_lay.addWidget(sub)
        lay.addWidget(header)

        content = QVBoxLayout()
        content.setContentsMargins(40, 25, 40, 40)
        content.setSpacing(12)

        try:
            from core.services.announcement_service import get_announcements
            notices = get_announcements(20)
        except:
            notices = []

        if notices:
            for n in notices:
                card = QFrame()
                card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 10px; }")

                cl = QVBoxLayout(card)
                cl.setContentsMargins(24, 20, 24, 20)
                cl.setSpacing(8)

                # Title row
                t_row = QHBoxLayout()
                is_imp = n.get("IsImportant", 0)

                if is_imp:
                    badge = QLabel("❗ Quan trọng")
                    badge.setStyleSheet("background: #FEF2F2; color: #DC2626; border-radius: 10px; padding: 2px 10px; font-size: 10px; font-weight: bold;")
                    t_row.addWidget(badge)

                t_lbl = QLabel(n.get("Title", ""))
                t_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
                t_lbl.setStyleSheet("color: #1A2B4C; border:none;")
                t_row.addWidget(t_lbl)
                t_row.addStretch()

                d_lbl = QLabel(n.get("CreatedAt", "")[:10])
                d_lbl.setStyleSheet("color: #A0AEC0; font-size: 11px; border:none;")
                t_row.addWidget(d_lbl)
                cl.addLayout(t_row)

                # Content
                c_text = n.get("Content", "")
                if c_text:
                    c_lbl = QLabel(c_text)
                    c_lbl.setWordWrap(True)
                    c_lbl.setStyleSheet("color: #4A5568; font-size: 12px; border:none;")
                    cl.addWidget(c_lbl)

                content.addWidget(card)
        else:
            no_lbl = QLabel("Chưa có thông báo nào.")
            no_lbl.setStyleSheet("color: #A0AEC0; font-size: 13px; padding: 30px;")
            no_lbl.setAlignment(Qt.AlignCenter)
            content.addWidget(no_lbl)

        content.addStretch()
        lay.addLayout(content)


# ══════════════════════════════════════════════════════════════════════════════
#  8. MESSAGES PAGE (Tin nhắn)
# ══════════════════════════════════════════════════════════════════════════════
class MessagesPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self.selected_staff = None
        self._build()

        self.timer = QTimer()
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start(10000)

    def _build(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # LEFT: danh sach nhan vien
        left = QFrame()
        left.setFixedWidth(280)
        left.setStyleSheet(
            "QFrame { background: white; border-right: 1px solid #E2E8F0; }")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(56)
        hdr.setStyleSheet("background: white; border-bottom: 1px solid #E2E8F0;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(16, 0, 16, 0)
        title = QLabel("💬 Tin nhắn")
        title.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        title.setStyleSheet("color: #1A2B4C; border: none;")
        hl.addWidget(title)
        hl.addStretch()
        ll.addWidget(hdr)

        # Staff list scroll
        self.staff_scroll = QScrollArea()
        self.staff_scroll.setWidgetResizable(True)
        self.staff_scroll.setFrameShape(QFrame.NoFrame)
        self.staff_scroll.setStyleSheet("background: transparent; border: none;")
        self.staff_container = QWidget()
        self.staff_container.setStyleSheet("background: transparent;")
        self.staff_layout = QVBoxLayout(self.staff_container)
        self.staff_layout.setContentsMargins(0, 0, 0, 0)
        self.staff_layout.setSpacing(0)
        self.staff_layout.addStretch()
        self.staff_scroll.setWidget(self.staff_container)
        ll.addWidget(self.staff_scroll)
        main.addWidget(left)

        # RIGHT: chat area
        right = QWidget()
        right.setStyleSheet("background: #F8FAFC;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # Chat header
        self.chat_header = QWidget()
        self.chat_header.setFixedHeight(56)
        self.chat_header.setStyleSheet(
            "background: white; border-bottom: 1px solid #E2E8F0;")
        chl = QHBoxLayout(self.chat_header)
        chl.setContentsMargins(20, 0, 20, 0)
        self.lbl_chat_name = QLabel("Chọn cuộc trò chuyện")
        self.lbl_chat_name.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
        self.lbl_chat_name.setStyleSheet("color: #1A2B4C; border: none;")
        self.lbl_chat_role = QLabel("")
        self.lbl_chat_role.setStyleSheet("color: #718096; font-size: 12px; border: none;")
        nc = QVBoxLayout(); nc.setSpacing(1)
        nc.addWidget(self.lbl_chat_name)
        nc.addWidget(self.lbl_chat_role)
        chl.addLayout(nc); chl.addStretch()
        rl.addWidget(self.chat_header)

        # Messages area
        self.msg_scroll = QScrollArea()
        self.msg_scroll.setWidgetResizable(True)
        self.msg_scroll.setFrameShape(QFrame.NoFrame)
        self.msg_scroll.setStyleSheet("background: transparent; border: none;")
        self.msg_container = QWidget()
        self.msg_container.setStyleSheet("background: transparent;")
        self.msg_layout = QVBoxLayout(self.msg_container)
        self.msg_layout.setContentsMargins(16, 12, 16, 12)
        self.msg_layout.setSpacing(4)
        self.msg_layout.addStretch()
        self.msg_scroll.setWidget(self.msg_container)
        rl.addWidget(self.msg_scroll)

        # Input bar
        input_bar = QWidget()
        input_bar.setFixedHeight(72)
        input_bar.setStyleSheet("background: white; border-top: 1px solid #E2E8F0;")
        il = QHBoxLayout(input_bar)
        il.setContentsMargins(16, 12, 16, 12)
        il.setSpacing(10)
        self.inp_msg = QLineEdit()
        self.inp_msg.setPlaceholderText("Nhập tin nhắn...")
        self.inp_msg.setFixedHeight(44)
        self.inp_msg.setStyleSheet("""
            QLineEdit {
                background: #F1F5F9; border: 1px solid #E2E8F0;
                border-radius: 8px; padding: 0 16px; font-size: 13px; color: #1A2B4C;
            }
            QLineEdit:focus { border: 1px solid #3B82F6; background: white; }
        """)
        self.inp_msg.returnPressed.connect(self._send)
        btn_send = QPushButton("Gửi ➤")
        btn_send.setFixedHeight(44)
        btn_send.setMinimumWidth(90)
        btn_send.setCursor(Qt.PointingHandCursor)
        btn_send.setStyleSheet("""
            QPushButton {
                background: #3B82F6; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #2563EB; }
        """)
        btn_send.clicked.connect(self._send)
        il.addWidget(self.inp_msg); il.addWidget(btn_send)
        rl.addWidget(input_bar)
        main.addWidget(right)

    def refresh(self):
        self._load_staff_list()

    def _load_staff_list(self):
        try:
            from core.services.message_service import get_student_conversations
            sid = self.portal.current_student.get("StudentID", "")
            self.all_staff = get_student_conversations(sid)
        except:
            self.all_staff = []
        self._render_staff()

    def _render_staff(self):
        # Clear old
        while self.staff_layout.count() > 1:
            item = self.staff_layout.takeAt(0)
            if item is None: break
            w = item.widget()
            if w: w.setParent(None); w.deleteLater()

        if not self.all_staff:
            no_lbl = QLabel("Chưa có tin nhắn nào.\nAdmin sẽ liên hệ bạn\nkhi cần thiết.")
            no_lbl.setAlignment(Qt.AlignCenter)
            no_lbl.setStyleSheet("color: #A0AEC0; font-size: 12px; padding: 30px; border: none;")
            self.staff_layout.insertWidget(0, no_lbl)
            return

        for s in self.all_staff:
            staff_id = s.get("StaffID", "")
            name = s.get("Name", "")
            role = "Quản trị viên" if s.get("Role") == "admin" else "Nhân viên"
            last_msg = s.get("LastMessage", "") or ""
            unread = s.get("UnreadCount", 0)

            item = QFrame()
            item.setCursor(Qt.PointingHandCursor)
            item.setFixedHeight(68)

            is_selected = self.selected_staff and self.selected_staff.get("StaffID") == staff_id
            if is_selected:
                item.setStyleSheet(
                    "QFrame { background: #EEF2FF; border-left: 3px solid #3B82F6;"
                    "border-bottom: 1px solid #E2E8F0; }")
            else:
                item.setStyleSheet(
                    "QFrame { background: transparent; border-bottom: 1px solid #F1F5F9; }"
                    "QFrame:hover { background: #F8FAFC; }")

            row = QHBoxLayout(item)
            row.setContentsMargins(12, 8, 12, 8)
            row.setSpacing(10)

            # Avatar
            initials = "".join(w[0] for w in name.split()[:2]).upper() or "NV"
            av = QLabel(initials)
            av.setFixedSize(38, 38)
            av.setAlignment(Qt.AlignCenter)
            av.setStyleSheet(
                "background: #EEF2FF; color: #4F46E5;"
                "border-radius: 19px; font-weight: bold; font-size: 12px; border: none;")
            row.addWidget(av)

            # Info
            info = QVBoxLayout(); info.setSpacing(2)
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                "color: #1A2B4C; font-weight: 600; font-size: 13px; border: none;")
            sub_text = last_msg[:35] + "..." if len(last_msg) > 35 else (last_msg or role)
            sub_lbl = QLabel(sub_text)
            sub_lbl.setStyleSheet("color: #718096; font-size: 11px; border: none;")
            info.addWidget(name_lbl)
            info.addWidget(sub_lbl)
            row.addLayout(info)
            row.addStretch()

            # Unread badge
            if unread > 0:
                badge = QLabel(str(unread))
                badge.setFixedSize(22, 22)
                badge.setAlignment(Qt.AlignCenter)
                badge.setStyleSheet(
                    "background: #EF4444; color: white;"
                    "border-radius: 11px; font-size: 11px; font-weight: bold; border: none;")
                row.addWidget(badge)

            item.mousePressEvent = lambda e, st=s: self._select_staff(st)
            self.staff_layout.insertWidget(self.staff_layout.count() - 1, item)

    def _select_staff(self, staff):
        self.selected_staff = staff
        staff_id = staff.get("StaffID", "")
        name = staff.get("Name", "")
        role = "Quản trị viên" if staff.get("Role") == "admin" else "Nhân viên"

        self.lbl_chat_name.setText(name)
        self.lbl_chat_role.setText(role)

        # Mark as read
        try:
            from core.services.message_service import mark_student_read
            sid = self.portal.current_student.get("StudentID", "")
            mark_student_read(sid, staff_id)
        except:
            pass

        self._load_messages()
        self._load_staff_list()

    def _load_messages(self):
        if not self.selected_staff:
            return
        from core.services.message_service import get_conversation
        staff_id = self.selected_staff.get("StaffID", "")
        student_id = self.portal.current_student.get("StudentID", "")

        msgs = get_conversation(staff_id, student_id)

        # Clear old messages
        while self.msg_layout.count() > 1:
            item = self.msg_layout.takeAt(0)
            if item is None: break
            w = item.widget()
            if w: w.setParent(None); w.deleteLater()

        if not msgs:
            no_msg = QLabel("Chưa có tin nhắn nào.\nHãy bắt đầu cuộc trò chuyện!")
            no_msg.setAlignment(Qt.AlignCenter)
            no_msg.setStyleSheet("color: #A0AEC0; font-size: 13px; border: none;")
            self.msg_layout.insertWidget(0, no_msg)
        else:
            from datetime import datetime as dt2
            idx = 0
            prev_dt = None
            for i, msg in enumerate(msgs):
                is_mine = msg.get("SenderType") == "student"
                sent_at = msg.get("SentAt", "")

                try:
                    cur_dt = dt2.strptime(sent_at, "%Y-%m-%d %H:%M:%S")
                except:
                    cur_dt = None

                # Time divider if gap > 15 min
                if cur_dt and prev_dt:
                    diff = (cur_dt - prev_dt).total_seconds() / 60
                    if diff >= 15:
                        time_str = cur_dt.strftime("%H:%M - %d/%m")
                        div = self._make_time_divider(time_str)
                        self.msg_layout.insertWidget(idx, div)
                        idx += 1
                elif cur_dt and not prev_dt:
                    time_str = cur_dt.strftime("%H:%M - %d/%m")
                    div = self._make_time_divider(time_str)
                    self.msg_layout.insertWidget(idx, div)
                    idx += 1

                # Show time on last message or before gap
                is_last = (i == len(msgs) - 1)
                show_time = is_last

                bubble = self._make_bubble(msg.get("Content", ""), sent_at, is_mine, show_time)
                self.msg_layout.insertWidget(idx, bubble)
                idx += 1
                prev_dt = cur_dt

        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.msg_scroll.verticalScrollBar().setValue(
            self.msg_scroll.verticalScrollBar().maximum()))

    def _make_time_divider(self, time_str):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 8, 0, 8); lay.setSpacing(8)
        line1 = QFrame(); line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("background: #E2E8F0; border: none;")
        lbl = QLabel(time_str)
        lbl.setStyleSheet(
            "color: #A0AEC0; font-size: 11px; border: none;"
            "background: transparent; padding: 0 6px;")
        lbl.setFixedHeight(16)
        line2 = QFrame(); line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("background: #E2E8F0; border: none;")
        lay.addWidget(line1, 1); lay.addWidget(lbl); lay.addWidget(line2, 1)
        return w

    def _make_bubble(self, content, sent_at, is_mine, show_time):
        frame = QFrame()
        frame.setStyleSheet("QFrame { border: none; background: transparent; }")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(8, 1, 8, 1)
        lay.setSpacing(2)

        bubble_row = QHBoxLayout()
        bubble_row.setContentsMargins(0, 0, 0, 0)

        MAX_W = 320
        from PyQt5.QtGui import QFontMetrics
        fm = QFontMetrics(QFont(FONT_FAMILY, 10))
        single_w = fm.horizontalAdvance(content) + 28
        actual_w = min(single_w, MAX_W)

        bubble = QLabel(content)
        bubble.setWordWrap(True)
        bubble.setFixedWidth(actual_w)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if is_mine:
            bubble.setStyleSheet(
                "background: #3B82F6; color: white;"
                "border-radius: 16px; border-bottom-right-radius: 4px;"
                "padding: 8px 12px; font-size: 13px; border: none;")
            bubble_row.addStretch()
            bubble_row.addWidget(bubble)
        else:
            bubble.setStyleSheet(
                "background: white; color: #1A2B4C;"
                "border-radius: 16px; border-bottom-left-radius: 4px;"
                "border: 1px solid #E2E8F0;"
                "padding: 8px 12px; font-size: 13px;")
            bubble_row.addWidget(bubble)
            bubble_row.addStretch()

        lay.addLayout(bubble_row)

        if show_time:
            try:
                from datetime import datetime as dt3
                dt_obj = dt3.strptime(sent_at, "%Y-%m-%d %H:%M:%S")
                time_str = dt_obj.strftime("%H:%M")
            except:
                time_str = sent_at or ""
            time_lbl = QLabel(time_str)
            time_lbl.setStyleSheet(
                "color: #A0AEC0; font-size: 11px; border: none; background: transparent;")
            time_lbl.setAlignment(Qt.AlignRight if is_mine else Qt.AlignLeft)
            lay.addWidget(time_lbl)

        return frame

    def _send(self):
        if not self.selected_staff:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn cuộc trò chuyện.")
            return
        content = self.inp_msg.text().strip()
        if not content:
            return

        from core.services.message_service import send_message
        student_id = self.portal.current_student.get("StudentID", "")
        staff_id = self.selected_staff.get("StaffID", "")

        send_message(student_id, "student", staff_id, "staff", content)
        self.inp_msg.clear()
        self._load_messages()
        self._load_staff_list()

    def _auto_refresh(self):
        if self.selected_staff:
            self._load_messages()
        self._load_staff_list()


# ══════════════════════════════════════════════════════════════════════════════
#  9. PROFILE PAGE (Hồ sơ cá nhân)
# ══════════════════════════════════════════════════════════════════════════════
class ProfilePage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _clear(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def _cl(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._cl(item.layout())

    def refresh(self):
        self._clear()
        lay = self.main_layout

        # Reload student data
        try:
            from core.services.student_service import get_student_by_id
            sid = self.portal.current_student.get("StudentID", "")
            student = get_student_by_id(sid)
            if student:
                self.portal.current_student = student
        except:
            student = self.portal.current_student

        name = student.get("Name", "Sinh viên")
        sid = student.get("StudentID", "")

        # Header
        header = QWidget()
        header.setStyleSheet("background: #1A2B4C;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(40, 25, 40, 25)

        h_row = QHBoxLayout()
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "SV"
        av = AvatarLabel(initials, "#F5C05B", "#1A2B4C", 60, 30)
        h_row.addWidget(av)
        h_row.addSpacing(16)

        v_info = QVBoxLayout()
        h1 = QLabel(name)
        h1.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        h1.setStyleSheet("color: white;")
        v_info.addWidget(h1)

        card_status = student.get("CardStatus", "active")
        status_text = "🟢 Thẻ đang hoạt động" if card_status == "active" else "🔴 Thẻ bị khóa"
        lbl_status = QLabel(f"MSSV: {sid} • {status_text}")
        lbl_status.setStyleSheet("color: #94A3B8; font-size: 12px;")
        v_info.addWidget(lbl_status)

        h_row.addLayout(v_info)
        h_row.addStretch()
        h_lay.addLayout(h_row)
        lay.addWidget(header)

        content = QHBoxLayout()
        content.setContentsMargins(40, 25, 40, 40)
        content.setSpacing(24)

        # Left: Thông tin cá nhân
        info_card = QFrame()
        info_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        ic_lay = QVBoxLayout(info_card)
        ic_lay.setContentsMargins(24, 24, 24, 24)
        ic_lay.setSpacing(14)

        ic_title = QLabel("👤 Thông tin cá nhân")
        ic_title.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        ic_title.setStyleSheet("color: #1A2B4C; border:none;")
        ic_lay.addWidget(ic_title)

        fields = [
            ("MSSV", sid),
            ("Họ và tên", name),
            ("Khoa", student.get("Faculty", "—")),
            ("Lớp", student.get("Class", "—")),
            ("Điện thoại", student.get("Phone", "—")),
            ("Email", student.get("Email", "—")),
            ("Hạn thẻ", student.get("CardExpire", "—")),
            ("Trạng thái", "Đang hoạt động" if card_status == "active" else "Bị khóa"),
        ]
        for label, value in fields:
            row = QHBoxLayout()
            l = QLabel(label)
            l.setFixedWidth(100)
            l.setStyleSheet("color: #718096; font-size: 12px; border:none;")
            v = QLabel(str(value))
            v.setStyleSheet("color: #2D3748; font-size: 12px; font-weight: bold; border:none;")
            row.addWidget(l)
            row.addWidget(v, 1)
            ic_lay.addLayout(row)

            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background: #F1F5F9; border:none;")
            ic_lay.addWidget(sep)

        content.addWidget(info_card, 1)

        # Right: Đổi mật khẩu
        pw_card = QFrame()
        pw_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        pc_lay = QVBoxLayout(pw_card)
        pc_lay.setContentsMargins(24, 24, 24, 24)
        pc_lay.setSpacing(14)

        pc_title = QLabel("🔒 Đổi mật khẩu")
        pc_title.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        pc_title.setStyleSheet("color: #1A2B4C; border:none;")
        pc_lay.addWidget(pc_title)

        input_style = "border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 12px;"

        self.inp_old_pw = QLineEdit()
        self.inp_old_pw.setPlaceholderText("Mật khẩu hiện tại")
        self.inp_old_pw.setEchoMode(QLineEdit.Password)
        self.inp_old_pw.setFixedHeight(38)
        self.inp_old_pw.setStyleSheet(input_style)
        pc_lay.addWidget(QLabel("Mật khẩu cũ:"))
        pc_lay.addWidget(self.inp_old_pw)

        self.inp_new_pw = QLineEdit()
        self.inp_new_pw.setPlaceholderText("Mật khẩu mới (ít nhất 6 ký tự)")
        self.inp_new_pw.setEchoMode(QLineEdit.Password)
        self.inp_new_pw.setFixedHeight(38)
        self.inp_new_pw.setStyleSheet(input_style)
        pc_lay.addWidget(QLabel("Mật khẩu mới:"))
        pc_lay.addWidget(self.inp_new_pw)

        self.inp_confirm_pw = QLineEdit()
        self.inp_confirm_pw.setPlaceholderText("Xác nhận mật khẩu mới")
        self.inp_confirm_pw.setEchoMode(QLineEdit.Password)
        self.inp_confirm_pw.setFixedHeight(38)
        self.inp_confirm_pw.setStyleSheet(input_style)
        pc_lay.addWidget(QLabel("Xác nhận:"))
        pc_lay.addWidget(self.inp_confirm_pw)

        btn_pw = QPushButton("Đổi mật khẩu")
        btn_pw.setFixedHeight(40)
        btn_pw.setCursor(Qt.PointingHandCursor)
        btn_pw.setStyleSheet("""
            QPushButton { background: #1A2B4C; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background: #0F172A; }
        """)
        btn_pw.clicked.connect(self._change_password)
        pc_lay.addWidget(btn_pw)
        pc_lay.addStretch()

        content.addWidget(pw_card, 1)
        lay.addLayout(content)

    def _change_password(self):
        old = self.inp_old_pw.text()
        new = self.inp_new_pw.text()
        confirm = self.inp_confirm_pw.text()

        if not old or not new:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ mật khẩu.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới và xác nhận không khớp.")
            return

        try:
            from core.services.student_service import change_student_password
            sid = self.portal.current_student.get("StudentID", "")
            ok, msg = change_student_password(sid, old, new)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
                self.inp_old_pw.clear()
                self.inp_new_pw.clear()
                self.inp_confirm_pw.clear()
            else:
                QMessageBox.warning(self, "Lỗi", msg)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  STUDENT PORTAL WINDOW (Main Window)
# ══════════════════════════════════════════════════════════════════════════════
class StudentPortalWindow(QWidget):
    def __init__(self, current_student=None, parent=None):
        super().__init__(parent)
        self.current_student = current_student or {}
        self.setWindowTitle(f"Student Portal — {APP_NAME}")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        self._build()
        self._center()
        self.show_page(0)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top Navigation Bar ────────────────────────────────────────────
        navbar = QWidget()
        navbar.setFixedHeight(56)
        navbar.setStyleSheet("background: #1A2B4C;")

        nav_lay = QHBoxLayout(navbar)
        nav_lay.setContentsMargins(24, 0, 24, 0)
        nav_lay.setSpacing(0)

        # Logo
        logo = QLabel("TV")
        logo.setFixedSize(32, 32)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("background: #F5C05B; color: #1A2B4C; font-weight: bold; border-radius: 4px;")
        nav_lay.addWidget(logo)
        nav_lay.addSpacing(10)

        logo_text = QLabel("ĐH Công nghệ Đông Á")
        logo_text.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
        logo_text.setStyleSheet("color: white;")
        logo_text.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        nav_lay.addWidget(logo_text)
        nav_lay.addSpacing(16)

        # Nav items (đã gỡ CSDL, Dịch vụ, Giới thiệu)
        self.nav_buttons = {}
        nav_items = [
            (0, "🏠 Trang chủ"),
            (1, "🔍 Tra cứu"),
            (3, "📊 Cá nhân"),
            (4, "📋 Lịch sử"),
            (5, "📝 Đề xuất"),
            (7, "💬 Tin nhắn"),
        ]
        for idx, label in nav_items:
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(56)
            btn.clicked.connect(lambda _, i=idx: self.show_page(i))
            self.nav_buttons[idx] = btn
            nav_lay.addWidget(btn)

        nav_lay.addStretch()

        # Chuông thông báo + tin nhắn chưa đọc
        try:
            from core.services.announcement_service import get_announcement_count
            ann_count = get_announcement_count()
        except:
            ann_count = 0
        try:
            from core.services.message_service import get_student_unread_count
            msg_count = get_student_unread_count(self.current_student.get("StudentID", ""))
        except:
            msg_count = 0

        total_badge = ann_count + msg_count
        bell_text = f"🔔 {total_badge}" if total_badge > 0 else "🔔"
        bell_btn = QPushButton(bell_text)
        bell_btn.setCursor(Qt.PointingHandCursor)
        bell_btn.setFixedHeight(32)
        bell_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15); color: white; font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 16px; padding: 0 14px; font-size: 13px;
            }
            QPushButton:hover { background: rgba(255, 255, 255, 0.25); border: 1px solid rgba(255, 255, 255, 0.4); }
        """)
        bell_btn.clicked.connect(lambda: self.show_page(6))
        nav_lay.addWidget(bell_btn)
        nav_lay.addSpacing(16)

        name = self.current_student.get("Name", "Sinh viên")
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "SV"

        avatar = AvatarLabel(initials, "rgba(255,255,255,0.25)", "white", 32, 12)
        nav_lay.addWidget(avatar)
        nav_lay.addSpacing(8)

        name_btn = QPushButton(name)
        name_btn.setCursor(Qt.PointingHandCursor)
        name_btn.setStyleSheet("""
            QPushButton { background: transparent; color: rgba(255,255,255,0.95); font-weight: bold; font-size: 13px; border: none; text-align: left; }
            QPushButton:hover { color: #F5C05B; text-decoration: underline; }
        """)
        name_btn.clicked.connect(lambda: self.show_page(8))
        nav_lay.addWidget(name_btn)
        nav_lay.addSpacing(16)

        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setFixedHeight(32)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: #F5C05B; color: #1A2B4C; border: none;
                border-radius: 6px; font-size: 11px; font-weight: bold; padding: 0 16px;
            }
            QPushButton:hover { background: #ECC94B; }
        """)
        btn_logout.clicked.connect(self._logout)
        nav_lay.addWidget(btn_logout)

        root.addWidget(navbar)

        # ── Stacked Pages ─────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #F8FAFC;")

        self.home_page = HomePage(self)
        self.explore_page = ExplorePage(self)
        self.book_detail_page = BookDetailPage(self)
        self.dashboard_page = StudentDashboard(self)
        self.history_page = BorrowHistoryPage(self)
        self.request_page = BookRequestPage(self)
        self.announce_page = AnnouncementsPage(self)
        self.messages_page = MessagesPage(self)
        self.profile_page = ProfilePage(self)

        self.stack.addWidget(self.home_page)        # 0
        self.stack.addWidget(self.explore_page)     # 1
        self.stack.addWidget(self.book_detail_page) # 2
        self.stack.addWidget(self.dashboard_page)   # 3
        self.stack.addWidget(self.history_page)     # 4
        self.stack.addWidget(self.request_page)     # 5
        self.stack.addWidget(self.announce_page)    # 6
        self.stack.addWidget(self.messages_page)    # 7
        self.stack.addWidget(self.profile_page)     # 8

        root.addWidget(self.stack, 1)

    def show_page(self, index):
        self.stack.setCurrentIndex(index)

        for idx, btn in self.nav_buttons.items():
            if idx == index:
                btn.setStyleSheet("""
                    QPushButton {
                        color: white; font-weight: bold; font-size: 12px;
                        border: none; border-bottom: 3px solid #F5C05B; padding: 0 12px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        color: rgba(255,255,255,0.7); font-size: 12px;
                        border: none; border-bottom: 3px solid transparent; padding: 0 12px;
                    }
                    QPushButton:hover {
                        color: white; border-bottom: 3px solid rgba(255,255,255,0.3);
                    }
                """)

        # Refresh data
        page_map = {
            0: self.home_page,
            1: self.explore_page,
            3: self.dashboard_page,
            4: self.history_page,
            5: self.request_page,
            6: self.announce_page,
            7: self.messages_page,
            8: self.profile_page,
        }
        page = page_map.get(index)
        if page and hasattr(page, 'refresh'):
            page.refresh()

    def _logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất",
            "Bạn có chắc muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                from shared.login_gui import UnifiedLoginWindow
                self.login = UnifiedLoginWindow()
            except:
                from user_app.gui.login_gui import LoginWindow
                self.login = LoginWindow()
            self.login.show()
            self.close()

    def _center(self):
        geo = QDesktopWidget().screenGeometry()
        self.move(
            (geo.width() - self.width()) // 2,
            (geo.height() - self.height()) // 2,
        )
