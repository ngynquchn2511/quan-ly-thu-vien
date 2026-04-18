# ── Student Portal GUI ─────────────────────────────────────────────────────
# Cổng thông tin sinh viên – PyQt5 Desktop App
# 4 trang: HomePage, ExplorePage, BookDetailPage, StudentDashboard
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QStackedWidget, QLineEdit, QScrollArea, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect, QRadioButton, QButtonGroup, QComboBox,
    QMessageBox, QDesktopWidget, QSpacerItem, QApplication, 
    QDialog, QDateEdit, QTimeEdit, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView
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
    "Ngoại ngữ":  {"bg": "#ECFDF5", "fg": "#059669", "icon": "🌐"},
    "Khoa học":   {"bg": "#FFFBEB", "fg": "#D97706", "icon": "🔬"},
    "Kinh tế":    {"bg": "#FFF1F2", "fg": "#E11D48", "icon": "📊"},
    "Toán học":   {"bg": "#F5F3FF", "fg": "#7C3AED", "icon": "📐"},
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

        container = QWidget()
        container.setStyleSheet("background: #F8FAFC;")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Hero Section ──────────────────────────────────────────────────
        hero = QWidget()
        hero.setMinimumHeight(320)
        hero.setObjectName("hero_bg")
        hero.setStyleSheet(f"""
            QWidget#hero_bg {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {GRADIENT_START}, stop:1 {GRADIENT_END}
                );
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
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

        sub = QLabel("120.000+ tài liệu - 15 cơ sở dữ liệu quốc tế - 45.000+ luận văn số hóa")
        sub.setFont(QFont(FONT_FAMILY, 10))
        sub.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent;")
        hero_lay.addWidget(sub)

        hero_lay.addSpacing(15)

        # Ô tìm kiếm
        search_row = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm sách, giáo trình, luận văn, tác giả...")
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

        hero_lay.addSpacing(10)

        # Quick links
        ql_lay = QHBoxLayout()
        ql_label = QLabel("Tìm nhanh:")
        ql_label.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px; background: transparent;")
        ql_lay.addWidget(ql_label)

        links = ["Luận văn thạc sĩ", "Giáo trình", "IEEE Xplore", "Tạp chí khoa học", "Sách mới"]
        for link in links:
            btn = QPushButton(link)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: rgba(255,255,255,0.9); 
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                }
                QPushButton:hover { background: rgba(255,255,255,0.15); }
            """)
            btn.clicked.connect(lambda checked, l=link: self._quick_search(l))
            ql_lay.addWidget(btn)
        
        ql_lay.addStretch()
        hero_lay.addLayout(ql_lay)

        hero_lay.addStretch()
        lay.addWidget(hero)

        # ── Layout chính cho content ──────────────────────────────────────────
        content_lay = QVBoxLayout()
        content_lay.setContentsMargins(40, 0, 40, 40)
        content_lay.setSpacing(24)

        # ── 1. Stat Cards (5 columns) ──────────────────────────────────────────
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: #F4F2EB;
                border-bottom: 2px solid #E2E8F0;
            }
        """)
        
        stats_lay = QHBoxLayout(stats_frame)
        stats_lay.setContentsMargins(40, 20, 40, 20)
        stats_lay.setSpacing(20)

        stat_items = [
            ("120.000+", "đầu sách & tài liệu"),
            ("15", "CSDL quốc tế"),
            ("45.000+", "luận văn số hóa"),
            ("T2 – T7", "7:30 – 21:00"),
            ("Miễn phí", "cho sinh viên ĐHCNĐÁ")
        ]
        
        for val, title in stat_items:
            vlay = QVBoxLayout()
            vlay.setSpacing(2)
            lbl_val = QLabel(val)
            lbl_val.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
            lbl_val.setStyleSheet("color: #1A2B4C; border: none; background: transparent;")
            vlay.addWidget(lbl_val)
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("color: #718096; font-size: 11px; border: none; background: transparent;")
            vlay.addWidget(lbl_title)
            
            stats_lay.addLayout(vlay)
            # Add separator except for last
            if title != stat_items[-1][1]:
                sep = QFrame()
                sep.setFixedWidth(1)
                sep.setStyleSheet("background: #CBD5E0; border: none;")
                stats_lay.addWidget(sep)
                
        lay.addWidget(stats_frame)

        # ── 2. CSDL & Tài liệu mới (2 columns) ─────────────────────────────────
        cols_lay = QHBoxLayout()
        cols_lay.setSpacing(20)

        # Trái: Tài liệu mới nhập
        tl_card = self._make_section_card("Tài liệu mới nhập kho", True)
        tl_vbox = QVBoxLayout()
        tl_vbox.setSpacing(0)
        
        new_docs = [
            ("Deep Learning — Goodfellow, Bengio", "Khoa học máy tính • NXB MIT Press 2024", "Mới"),
            ("Giáo trình Cơ học kết cấu T.3", "Xây dựng • NXB ĐHCNĐÁ 2024", "Mới"),
            ("Clean Architecture — Robert C. Martin", "Công nghệ phần mềm • 2024", "Mới"),
            ("Lý thuyết điều khiển tự động", "Điện - Điện tử • Tái bản lần 5", "Mới")
        ]
        
        for t_main, t_sub, badge in new_docs:
            row = QHBoxLayout()
            doc_lay = QVBoxLayout()
            doc_lay.setSpacing(2)
            lbl_main = QLabel(t_main)
            lbl_main.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
            lbl_main.setStyleSheet("color: #2D3748; border: none;")
            
            lbl_sub = QLabel(t_sub)
            lbl_sub.setStyleSheet("color: #718096; font-size: 10px; border: none;")
            
            doc_lay.addWidget(lbl_main)
            doc_lay.addWidget(lbl_sub)
            row.addLayout(doc_lay)
            
            if badge:
                lbl_badge = QLabel(badge)
                lbl_badge.setStyleSheet("""
                    background: #ECFDF5;
                    color: #059669;
                    border-radius: 10px;
                    padding: 2px 8px;
                    font-size: 10px;
                    font-weight: bold;
                """)
                lbl_badge.setAlignment(Qt.AlignCenter)
                lbl_badge.setFixedSize(40, 20)
                row.addWidget(lbl_badge)
                
            frame = ClickableFrame()
            frame.setCursor(Qt.PointingHandCursor)
            frame.setStyleSheet("QFrame { border-bottom: 1px solid #E2E8F0; } QFrame:hover { background: #F1F5F9; }")
            frame.clicked.connect(lambda _=False, t=t_main: self._quick_search(t))
            frame.setLayout(row)
            tl_vbox.addWidget(frame)
            
        more_btn = QPushButton("Xem tất cả tài liệu mới →")
        more_btn.setStyleSheet("color: #D97706; font-size: 11px; text-align: left; border: none; padding: 10px 0;")
        more_btn.setCursor(Qt.PointingHandCursor)
        more_btn.clicked.connect(lambda: self.portal.show_page(1))
        tl_vbox.addWidget(more_btn)
        
        tl_card.layout().addLayout(tl_vbox)
        cols_lay.addWidget(tl_card, 1)

        # Phải: CSDL trực tuyến
        csdl_card = self._make_section_card("Cơ sở dữ liệu trực tuyến", True)
        csdl_vbox = QVBoxLayout()
        csdl_vbox.setSpacing(0)
        
        dbs = [
            ("IEEE Xplore", "Kỹ thuật điện, điện tử, CNTT", "Truy cập", "#ECFDF5", "#059669"),
            ("Springer Nature", "Khoa học tự nhiên, kỹ thuật", "Truy cập", "#ECFDF5", "#059669"),
            ("ScienceDirect", "Tạp chí Elsevier đa ngành", "Truy cập", "#ECFDF5", "#059669"),
            ("ProQuest", "Luận văn, tạp chí khoa học", "Cần VPN", "#FEF3C7", "#D97706")
        ]
        
        for name, sub, badge_text, badge_bg, badge_fg in dbs:
            row = QHBoxLayout()
            doc_lay = QVBoxLayout()
            doc_lay.setSpacing(2)
            lbl = QLabel(name)
            lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
            lbl.setStyleSheet("color: #2D3748; border: none;")
            doc_lay.addWidget(lbl)
            
            lbl_s = QLabel(sub)
            lbl_s.setStyleSheet("color: #718096; font-size: 10px; border: none;")
            doc_lay.addWidget(lbl_s)
            row.addLayout(doc_lay)
            
            badge = QPushButton(badge_text)
            badge.setFixedSize(60, 24)
            badge.setCursor(Qt.PointingHandCursor)
            badge.setStyleSheet(f"""
                QPushButton {{
                    background: {badge_bg};
                    color: {badge_fg};
                    border-radius: 12px;
                    font-size: 10px;
                    font-weight: bold;
                    border: none;
                }}
                QPushButton:hover {{ background: {badge_fg}; color: white; }}
            """)
            url_map = {
                "IEEE Xplore": "https://ieeexplore.ieee.org/",
                "Springer Nature": "https://link.springer.com/",
                "ScienceDirect": "https://www.sciencedirect.com/",
                "ProQuest": "https://www.proquest.com/"
            }
            badge.clicked.connect(lambda _=False, nm=name, u=url_map: QDesktopServices.openUrl(QUrl(u.get(nm))))
            row.addWidget(badge)
            
            frame = QFrame()
            frame.setStyleSheet("border-bottom: 1px solid #E2E8F0;")
            frame.setLayout(row)
            csdl_vbox.addWidget(frame)
        
        more_db = QPushButton("Xem tất cả CSDL →")
        more_db.setStyleSheet("color: #D97706; font-size: 11px; text-align: left; border: none; padding: 10px 0;")
        more_db.setCursor(Qt.PointingHandCursor)
        more_db.clicked.connect(lambda: self.portal.show_page(2))
        csdl_vbox.addWidget(more_db)
        
        csdl_card.layout().addLayout(csdl_vbox)
        cols_lay.addWidget(csdl_card, 1)
        
        content_lay.addLayout(cols_lay)

        # ── 3. Duyệt theo lĩnh vực ──────────────────────────────────────────────
        lv_lbl = QLabel("Duyệt theo lĩnh vực")
        lv_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        lv_lbl.setStyleSheet("color: #1A2B4C;")
        content_lay.addWidget(lv_lbl)
        
        lv_lay = QGridLayout()
        lv_lay.setSpacing(12)
        
        tags = [
            "Công nghệ thông tin", "Điện - Điện tử", "Cơ khí & chế tạo", "Xây dựng",
            "Hóa học & CNTP", "Vật lý kỹ thuật", "Kinh tế & quản lý", "Toán & ứng dụng",
            "Ngoại ngữ", "Khoa học vật liệu", "Môi trường", "Cơ điện tử"
        ]
        
        r, c = 0, 0
        for tag in tags:
            btn = QPushButton(tag)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    color: #4A5568;
                    border: 1px solid #E2E8F0;
                    border-radius: 15px;
                    padding: 0 16px;
                    font-size: 11px;
                }
                QPushButton:hover { border-color: #A0AEC0; color: #1A2B4C; }
            """)
            btn.clicked.connect(lambda checked, t=tag: self._quick_search(t))
            lv_lay.addWidget(btn, r, c)
            c += 1
            if c > 7:
                c = 0
                r += 1
                
        # Fill empty space
        empty_lbl = QLabel()
        lv_lay.addWidget(empty_lbl, r, c, 1, 8-c)
        content_lay.addLayout(lv_lay)

        # Thêm separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #E2E8F0;")
        content_lay.addWidget(sep)

        # ── 4. Thông báo ────────────────────────────────────────────────────────
        tb_card = self._make_section_card("Thông báo & sự kiện", False)
        # them nut xem tat ca
        tb_card.layout().itemAt(0).widget().hide() # Hide old title to make a horizontal header
        tb_header = QHBoxLayout()
        th = QLabel("Thông báo & sự kiện")
        th.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        th.setStyleSheet("color: #1A2B4C;")
        tb_header.addWidget(th)
        tb_header.addStretch()
        more_th = QPushButton("Xem tất cả")
        more_th.setStyleSheet("color: #D97706; font-size: 11px; border:none;")
        more_th.setCursor(Qt.PointingHandCursor)
        more_th.clicked.connect(lambda: self.portal.show_page(2)) # Navigate to CSDL as a placeholder
        tb_header.addWidget(more_th)
        tb_card.layout().insertLayout(0, tb_header)
        
        tb_vbox = QVBoxLayout()
        tb_vbox.setSpacing(0)
        
        notices = [
            ("Quan trọng", "#FEF2F2", "#DC2626", "Hạn trả sách kỳ học được gia hạn đến 20/05/2026", "14/04/2026"),
            ("18/04", "#EFF6FF", "#2563EB", "Hướng dẫn sử dụng CSDL Springer Nature — Phòng đào tạo số hóa tầng 3, 14:00\nĐăng ký tham dự tại quầy thư viện", ""),
            ("Mới", "#ECFDF5", "#059669", "Bổ sung 200 đầu giáo trình cho học kỳ hè 2026", "10/04/2026"),
            ("Thứ Bảy", "#FEF3C7", "#D97706", "Câu lạc bộ nghiên cứu khoa học - 9:00 sáng, phòng sinh hoạt tầng 1", "")
        ]
        
        for badge_t, bg, fg, text, subtext in notices:
            row = QHBoxLayout()
            row.setContentsMargins(10, 15, 10, 15)
            badge = QLabel(badge_t)
            badge.setFixedSize(60, 24)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(f"""
                background: {bg};
                color: {fg};
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            """)
            
            row.addWidget(badge, alignment=Qt.AlignTop)
            row.addSpacing(16)
            
            vlay = QVBoxLayout()
            vlay.setSpacing(4)
            lbl = QLabel(text)
            lbl.setFont(QFont(FONT_FAMILY, 11))
            lbl.setStyleSheet("color: #2D3748; border: none;")
            vlay.addWidget(lbl)
            if subtext:
                lbls = QLabel(subtext)
                lbls.setStyleSheet("color: #A0AEC0; font-size: 10px; border:none;")
                vlay.addWidget(lbls)
            
            row.addLayout(vlay)
            row.addStretch()
            
            frame = ClickableFrame()
            frame.setCursor(Qt.PointingHandCursor)
            frame.setStyleSheet("QFrame { border-bottom: 1px solid #E2E8F0; } QFrame:hover { background: #F1F5F9; }")
            frame.setLayout(row)
            frame.clicked.connect(lambda _=False, t=text, st=subtext: QMessageBox.information(self, "Thông báo", f"{t}\n\nThời gian: {st if st else 'N/A'}"))
            tb_vbox.addWidget(frame)
            
        tb_card.layout().addLayout(tb_vbox)
        content_lay.addWidget(tb_card)

        content_lay.addStretch()
        lay.addLayout(content_lay)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_section_card(self, title, with_border=False):
        card = QFrame()
        if with_border:
            card.setStyleSheet("""
                QFrame {
                    background: white;
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                }
            """)
        else:
            card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 8px; }")
            
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 10)
        lay.setSpacing(10)
        
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
        title_lbl.setStyleSheet("color: #1A2B4C; border: none;")
        lay.addWidget(title_lbl)
        
        return card

    def _quick_search(self, kw):
        if hasattr(self.portal, 'explore_page'):
            self.portal.explore_page.set_keyword(kw)
            self.portal.show_page(1)

    def _do_search(self):
        kw = self.inp_search.text().strip()
        if hasattr(self.portal, 'explore_page'):
            self.portal.explore_page.set_keyword(kw)
            self.portal.show_page(1)

    def refresh(self):
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  2. EXPLORE PAGE (Tra cứu tài liệu)
# ══════════════════════════════════════════════════════════════════════════════
class ExplorePage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
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

        # Thanh tìm kiếm trên cùng
        top_bar = QWidget()
        top_bar.setStyleSheet("background: #1A2B4C;")
        t_lay = QVBoxLayout(top_bar)
        t_lay.setContentsMargins(40, 20, 40, 20)
        
        search_row = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm kiếm...")
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
        
        # Thẻ filter nhanh
        filter_row = QHBoxLayout()
        filters = ["Tất cả", "Sách", "Giáo trình", "Luận văn / Luận án", "Tạp chí khoa học", "Tài liệu số"]
        self.active_filter = "Tất cả"
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

        # ── Main Content 2 cols ──────────────────────────────────────────────
        main_lay = QHBoxLayout()
        main_lay.setContentsMargins(40, 30, 40, 40)
        main_lay.setSpacing(30)

        # Left Column: Danh sách kết quả (vertical)
        left_col = QVBoxLayout()
        self.lbl_count = QLabel("Hiển thị 0 trong 0 kết quả")
        self.lbl_count.setStyleSheet("color: #718096; font-size: 11px;")
        left_col.addWidget(self.lbl_count)
        
        self.v_list = QVBoxLayout()
        self.v_list.setSpacing(12)
        self.v_list.setAlignment(Qt.AlignTop)
        
        left_col.addLayout(self.v_list)
        left_col.addStretch()
        
        main_lay.addLayout(left_col, 3)

        # Right Column: Lọc kết quả
        right_col = QVBoxLayout()
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        fc_lay = QVBoxLayout(filter_card)
        fc_lay.setContentsMargins(20, 20, 20, 20)
        fc_lay.setSpacing(15)
        
        flbl = QLabel("Lọc kết quả")
        flbl.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        flbl.setStyleSheet("border:none;")
        fc_lay.addWidget(flbl)
        
        # Loai tai lieu
        type_lbl = QLabel("LOẠI TÀI LIỆU")
        type_lbl.setStyleSheet("color: #718096; font-size: 10px; font-weight: bold; border:none;")
        fc_lay.addWidget(type_lbl)
        fc_lay.addWidget(QRadioButton("Sách (312)"))
        fc_lay.addWidget(QRadioButton("Luận văn (245)"))
        fc_lay.addWidget(QRadioButton("Tạp chí (180)"))
        
        fc_lay.addSpacing(10)
        lang_lbl = QLabel("NGÔN NGỮ")
        lang_lbl.setStyleSheet("color: #718096; font-size: 10px; font-weight: bold; border:none;")
        fc_lay.addWidget(lang_lbl)
        fc_lay.addWidget(QRadioButton("Tiếng Anh (610)"))
        fc_lay.addWidget(QRadioButton("Tiếng Việt (237)"))
        
        fc_lay.addSpacing(10)
        st_lbl = QLabel("TÌNH TRẠNG")
        st_lbl.setStyleSheet("color: #718096; font-size: 10px; font-weight: bold; border:none;")
        fc_lay.addWidget(st_lbl)
        fc_lay.addWidget(QRadioButton("Còn sẵn trên kệ"))
        r2 = QRadioButton("Tất cả")
        r2.setChecked(True)
        fc_lay.addWidget(r2)
        
        right_col.addWidget(filter_card)
        
        # Linh vuc card
        lv_card = QFrame()
        lv_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        lv_lay = QVBoxLayout(lv_card)
        lv_lay.setContentsMargins(20, 20, 20, 20)
        lv_lay.setSpacing(10)
        
        lvlbl = QLabel("Lĩnh vực")
        lvlbl.setStyleSheet("color: #718096; font-size: 10px; font-weight: bold; border:none;")
        lv_lay.addWidget(lvlbl)
        lv_lay.addWidget(QRadioButton("CNTT (412)"))
        lv_lay.addWidget(QRadioButton("Điện tử (95)"))
        lv_lay.addWidget(QRadioButton("Toán học (84)"))
        
        right_col.addWidget(lv_card)
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
        try:
            from core.services.book_service import search_books
            books = search_books(kw, "", "", "all")
            if hasattr(self, 'active_filter') and self.active_filter != "Tất cả":
                f_kw = self.active_filter.lower()
                filtered = []
                for b in books:
                    cat = b.get("Category", "").lower()
                    title = b.get("Title", "").lower()
                    if self.active_filter == "Sách" and ("sách" in cat or "sách" in title):
                        filtered.append(b)
                    elif self.active_filter == "Giáo trình" and ("giáo" in cat or "trình" in cat):
                        filtered.append(b)
                    elif self.active_filter == "Luận văn / Luận án" and ("luận" in cat or "án" in cat or "luận" in title):
                        filtered.append(b)
                    elif self.active_filter == "Tạp chí khoa học" and ("tạp chí" in cat or "báo chí" in cat or "tạp" in title):
                        filtered.append(b)
                    elif self.active_filter == "Tài liệu số" and ("tài liệu" in cat or "số" in cat):
                        filtered.append(b)
                books = filtered
            self._display_books(books)
        except: pass

    def _display_books(self, books):
        while self.v_list.count():
            item = self.v_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.lbl_count.setText(f"Hiển thị 1–{len(books)} trong {len(books)} kết quả cho \"{self.inp_search.text()}\"")

        for book in books:
            card = self._make_list_item(book)
            self.v_list.addWidget(card)

    def _make_list_item(self, book):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        card.setFixedHeight(110)
        
        lay = QHBoxLayout(card)
        lay.setContentsMargins(20, 15, 20, 15)
        lay.setSpacing(15)
        
        # Left: Cover placeholder
        cover = QLabel(book.get("Title", "B")[0:2].upper())
        cover.setFixedSize(50, 70)
        cover.setAlignment(Qt.AlignCenter)
        cover.setStyleSheet("background: #1A2B4C; color: #F5C05B; font-weight: bold; border-radius: 4px; font-size: 14px;")
        lay.addWidget(cover)
        
        # Mid: Info
        mid = QVBoxLayout()
        mid.setSpacing(4)
        title = QLabel(book.get("Title", ""))
        title.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        title.setStyleSheet("color: #1A2B4C; border: none;")
        mid.addWidget(title)
        
        author = QLabel(f"{book.get('Author', '')} • {book.get('Category', '')} • {book.get('PublishYear', '2020')}")
        author.setStyleSheet("color: #718096; font-size: 11px; border: none;")
        mid.addWidget(author)
        
        tags_lay = QHBoxLayout()
        tags = ["Sách tham khảo", "Tiếng Anh", "Học máy"]
        for t in tags:
            tag = QLabel(t)
            tag.setStyleSheet("background: #EBF8FF; color: #3182CE; padding: 2px 8px; border-radius: 4px; font-size: 10px; border:none;")
            tags_lay.addWidget(tag)
        tags_lay.addStretch()
        mid.addLayout(tags_lay)
        lay.addLayout(mid, 1)
        
        # Right: Buttons
        right = QVBoxLayout()
        right.setSpacing(6)
        
        b1 = QPushButton("Đặt mượn")
        b1.setCursor(Qt.PointingHandCursor)
        b1.setStyleSheet("background: #1A2B4C; color: white; border-radius: 6px; padding: 6px 16px; font-size: 11px; font-weight: bold;")
        b1.clicked.connect(lambda _, b=book: self._open_book(b))
        
        b2 = QPushButton("Xem chi tiết")
        b2.setCursor(Qt.PointingHandCursor)
        b2.setStyleSheet("background: white; color: #4A5568; border: 1px solid #CBD5E0; border-radius: 6px; padding: 6px 16px; font-size: 11px;")
        b2.clicked.connect(lambda _, b=book: self._open_book(b))
        
        right.addWidget(b1)
        right.addWidget(b2)
        right.addStretch()
        lay.addLayout(right)
        
        return card

    def _open_book(self, book):
        if hasattr(self.portal, 'book_detail_page'):
            self.portal.book_detail_page.load_book(book)
            self.portal.show_page(5)

    def refresh(self):
        self._search()


# ══════════════════════════════════════════════════════════════════════════════
#  3. CSDL TRỰC TUYẾN
# ══════════════════════════════════════════════════════════════════════════════
class CSDLPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

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

        # Header
        top_bar = QWidget()
        top_bar.setStyleSheet("background: #1A2B4C;")
        t_lay = QVBoxLayout(top_bar)
        t_lay.setContentsMargins(40, 30, 40, 30)
        
        lbl1 = QLabel("NGUỒN TÀI NGUYÊN HỌC THUẬT")
        lbl1.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px; font-weight: bold;")
        t_lay.addWidget(lbl1)
        
        lbl2 = QLabel("Cơ sở dữ liệu <span style='color:#F5C05B;font-style:italic;'>trực tuyến</span>")
        lbl2.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        lbl2.setStyleSheet("color: white;")
        t_lay.addWidget(lbl2)
        
        lbl3 = QLabel("Truy cập miễn phí trong campus • Một số CSDL yêu cầu VPN khi truy cập ngoài trường")
        lbl3.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")
        t_lay.addWidget(lbl3)
        lay.addWidget(top_bar)

        # Cards area
        main_lay = QVBoxLayout()
        main_lay.setContentsMargins(40, 30, 40, 40)
        main_lay.setSpacing(30)
        
        sections = [
            ("Kỹ thuật & Công nghệ", [
                ("IEEE", "IEEE Xplore", "Hơn 5 triệu tài liệu về kỹ thuật điện, điện tử, tính toán.", "5M+ tài liệu", "Truy cập trong campus", "#ECFDF5", "#059669"),
                ("ACM", "ACM Digital Library", "Kho tài nguyên hàng đầu về khoa học máy tính.", "600K+ tài liệu", "Truy cập trong campus", "#ECFDF5", "#059669"),
                ("SD", "ScienceDirect", "Tạp chí và sách của Elsevier đa ngành từ kỹ thuật đến y sinh.", "18M+ bài báo", "Truy cập trong campus", "#ECFDF5", "#059669")
            ]),
            ("Khoa học & Nghiên cứu", [
                ("SN", "Springer Nature", "Sách và tạp chí khoa học tự nhiên, kỹ thuật, toán học.", "3K+ tạp chí", "Truy cập trong campus", "#ECFDF5", "#059669"),
                ("SC", "Scopus", "Cơ sở dữ liệu trích dẫn lớn nhất thế giới, hỗ trợ H-index.", "90M+ bản ghi", "Cần VPN ngoài campus", "#FEF3C7", "#D97706"),
                ("PQ", "ProQuest", "Luận văn, luận án quốc tế và tạp chí đa ngành.", "6M+ luận văn", "Cần VPN ngoài campus", "#FEF3C7", "#D97706")
            ]),
            ("Tài nguyên mở & trong nước", [
                ("arX", "arXiv.org", "Preprint miễn phí về toán, vật lý, CNTT, thống kê.", "2M+ preprints", "Miễn phí", "#ECFDF5", "#059669"),
                ("VN", "Luận văn ĐHCN Đông Á", "Kho luận văn, luận án của trường số hóa từ 2000.", "45K+ tài liệu", "Truy cập nội bộ", "#ECFDF5", "#059669"),
                ("VN2", "CSDL Luận văn Quốc gia", "Hệ thống chung của các trường đại học.", "200K+ tài liệu", "Miễn phí", "#ECFDF5", "#059669")
            ])
        ]
        
        for sec_name, items in sections:
            lbl = QLabel(sec_name)
            lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
            lbl.setStyleSheet("color: #1A2B4C;")
            main_lay.addWidget(lbl)
            
            row = QHBoxLayout()
            row.setSpacing(20)
            for ic, nm, d, sub, bg_text, b_bg, b_fg in items:
                c = ClickableFrame()
                c.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; } QFrame:hover { border: 1px solid #A0AEC0; }")
                c.setFixedHeight(140)
                c.setCursor(Qt.PointingHandCursor)
                url_map = {
                    "IEEE Xplore": "https://ieeexplore.ieee.org/",
                    "ACM Digital Library": "https://dl.acm.org/",
                    "ScienceDirect": "https://www.sciencedirect.com/",
                    "Springer Nature": "https://link.springer.com/",
                    "Scopus": "https://www.scopus.com/",
                    "ProQuest": "https://www.proquest.com/",
                    "arXiv.org": "https://arxiv.org/",
                    "Luận văn ĐHCN Đông Á": "http://thuvien.eaut.edu.vn",
                    "CSDL Luận văn Quốc gia": "http://luanvan.moet.gov.vn"
                }
                c.clicked.connect(lambda _=False, nm_val=nm, u=url_map: QDesktopServices.openUrl(QUrl(u.get(nm_val, "https://google.com/search?q="+nm_val))))
                
                cl = QVBoxLayout(c)
                cl.setContentsMargins(20, 20, 20, 20)
                cl.setSpacing(10)
                
                # icon
                icl = QLabel(ic)
                icl.setFixedSize(40, 30)
                icl.setAlignment(Qt.AlignCenter)
                icl.setStyleSheet("background: #F8FAFC; color: #4A5568; border-radius: 4px; font-weight:bold; font-size: 11px; border:none;")
                cl.addWidget(icl)
                
                nml = QLabel(nm)
                nml.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
                nml.setStyleSheet("color: #1A2B4C; border:none;")
                cl.addWidget(nml)
                
                dl = QLabel(d)
                dl.setStyleSheet("color: #718096; font-size: 11px; border:none;")
                dl.setWordWrap(True)
                cl.addWidget(dl)
                
                cl.addStretch()
                
                # footer
                f_row = QHBoxLayout()
                sl = QLabel(sub)
                sl.setStyleSheet("color: #A0AEC0; font-size: 10px; border:none;")
                f_row.addWidget(sl)
                f_row.addStretch()
                
                bl = QLabel(bg_text)
                bl.setStyleSheet(f"background: {b_bg}; color: {b_fg}; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; border:none;")
                f_row.addWidget(bl)
                
                cl.addLayout(f_row)
                row.addWidget(c)
                
            main_lay.addLayout(row)
            
        main_lay.addStretch()
        lay.addLayout(main_lay)
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ══════════════════════════════════════════════════════════════════════════════
#  4. DỊCH VỤ THƯ VIỆN
# ══════════════════════════════════════════════════════════════════════════════
class DichVuPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

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

        # Header
        top_bar = QWidget()
        top_bar.setStyleSheet("background: #1A2B4C;")
        t_lay = QVBoxLayout(top_bar)
        t_lay.setContentsMargins(40, 30, 40, 30)
        
        lbl1 = QLabel("HỖ TRỢ HỌC TẬP & NGHIÊN CỨU")
        lbl1.setStyleSheet("color: #F5C05B; font-size: 11px; font-weight: bold;")
        t_lay.addWidget(lbl1)
        
        lbl2 = QLabel("Dịch vụ <span style='font-style:italic;'>thư viện</span>")
        lbl2.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        lbl2.setStyleSheet("color: white;")
        t_lay.addWidget(lbl2)
        
        lbl3 = QLabel("Đặt phòng • In ấn • Tư vấn nghiên cứu • Hỗ trợ trích dẫn")
        lbl3.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")
        t_lay.addWidget(lbl3)
        lay.addWidget(top_bar)

        # Cards area
        main_lay = QVBoxLayout()
        main_lay.setContentsMargins(40, 30, 40, 40)
        main_lay.setSpacing(30)
        
        sections = [
            ("Không gian học tập", [
                ("Phòng đọc cá nhân", "Khu đọc sách yên tĩnh tầng 2 & 3. Sức chứa 400 chỗ."),
                ("Phòng học nhóm", "8 phòng học nhóm 4-10 người. Đặt trước trực tuyến."),
                ("Phòng máy tính", "80 máy tính có internet, phần mềm kỹ thuật (MATLAB).")
            ]),
            ("Hỗ trợ nghiên cứu", [
                ("Tư vấn nghiên cứu", "Hướng dẫn tìm tài liệu, chiến lược tìm kiếm."),
                ("Hỗ trợ trích dẫn", "Sử dụng EndNote, Mendeley, Zotero chuẩn APA, IEEE."),
                ("Kiểm tra đạo văn", "Hệ thống Turnitin và iThenticate dành cho SV.")
            ]),
            ("Tiện ích khác", [
                ("Dịch vụ in & scan", "500đ/A4 đen trắng. Máy tự động phục vụ tại tầng 1."),
                ("Hỏi đáp trực tuyến", "Chat với thủ thư hành chính. Phản hồi trong 2 giờ."),
                ("Tủ khóa cá nhân", "Thuê tủ khóa. Đặt cọc 50K hoàn trả khi trả chìa.")
            ])
        ]
        
        for sec_name, items in sections:
            lbl = QLabel(sec_name)
            lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
            lbl.setStyleSheet("color: #1A2B4C;")
            main_lay.addWidget(lbl)
            
            row = QHBoxLayout()
            row.setSpacing(20)
            for nm, d in items:
                c = ClickableFrame()
                c.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; } QFrame:hover { border: 1px solid #A0AEC0; }")
                c.setFixedHeight(120)
                c.setCursor(Qt.PointingHandCursor)
                c.clicked.connect(lambda _=False, _nm=nm, _d=d: QMessageBox.information(self, "Dịch vụ", f"{_nm}\n\n{_d}"))
                
                cl = QVBoxLayout(c)
                cl.setContentsMargins(20, 20, 20, 20)
                
                nml = QLabel(nm)
                nml.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
                nml.setStyleSheet("color: #1A2B4C; border:none;")
                cl.addWidget(nml)
                
                dl = QLabel(d)
                dl.setStyleSheet("color: #718096; font-size: 11px; border:none;")
                dl.setWordWrap(True)
                cl.addWidget(dl)
                cl.addStretch()
                row.addWidget(c)
                
            main_lay.addLayout(row)
            
        main_lay.addStretch()
        lay.addLayout(main_lay)
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ══════════════════════════════════════════════════════════════════════════════
#  5. GIỚI THIỆU
# ══════════════════════════════════════════════════════════════════════════════
class GioiThieuPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

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

        # Header
        top_bar = QWidget()
        top_bar.setStyleSheet("background: #1A2B4C;")
        t_lay = QVBoxLayout(top_bar)
        t_lay.setContentsMargins(40, 30, 40, 30)
        
        lbl1 = QLabel("VỀ CHÚNG TÔI")
        lbl1.setStyleSheet("color: #F5C05B; font-size: 11px; font-weight: bold;")
        t_lay.addWidget(lbl1)
        
        lbl2 = QLabel("Thư viện <span style='font-style:italic; color:#F5C05B;'>Đại học Công nghệ Đông Á</span>")
        lbl2.setFont(QFont(FONT_FAMILY, 20, QFont.Bold))
        lbl2.setStyleSheet("color: white;")
        t_lay.addWidget(lbl2)
        
        lbl3 = QLabel("Phục vụ cộng đồng học thuật Đại học Công nghệ Đông Á")
        lbl3.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")
        t_lay.addWidget(lbl3)
        lay.addWidget(top_bar)

        # 2 Cols Content
        main_lay = QHBoxLayout()
        main_lay.setContentsMargins(40, 30, 40, 40)
        main_lay.setSpacing(30)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        
        def dict_to_card(title, pd):
            c = QFrame()
            c.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
            cl = QVBoxLayout(c)
            cl.setContentsMargins(20, 20, 20, 20)
            
            tl = QLabel(title)
            tl.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
            tl.setStyleSheet("color: #1A2B4C; border:none;")
            cl.addWidget(tl)
            cl.addSpacing(10)
            
            for k, v in pd.items():
                r = QHBoxLayout()
                lblk = QLabel(k)
                lblk.setFixedWidth(100)
                lblk.setStyleSheet("color: #718096; font-size: 11px; border:none;")
                lblv = QLabel(v)
                lblv.setStyleSheet("color: #2D3748; font-size: 11px; border:none; font-weight: bold;")
                r.addWidget(lblk)
                r.addWidget(lblv)
                cl.addLayout(r)
                
                f = QFrame()
                f.setFixedHeight(1)
                f.setStyleSheet("background: #E2E8F0; border:none;")
                cl.addWidget(f)
            return c
            
        gio = {"Thứ Hai – Thứ Sáu": "7:30 – 21:00", "Thứ Bảy": "7:30 – 17:00", "Chủ Nhật": "Đóng cửa", "Ngày lễ": "Đóng cửa"}
        left_col.addWidget(dict_to_card("Giờ mở cửa", gio))
        
        muon = {"Sinh viên ĐH": "5 quyển / 30 ngày / Gia hạn 1 lần", "Sinh viên THS/TS": "8 quyển / 60 ngày / Gia hạn 2 lần", "Giảng viên": "10 quyển / 90 ngày", "Phí quá hạn": "1.000đ / quyển / ngày"}
        left_col.addWidget(dict_to_card("Quy định mượn trả", muon))
        
        lien = {"Địa chỉ": "Đại học Công nghệ Đông Á", "Điện thoại": "(024) 3869 2354", "Email": "library@eaut.edu.vn"}
        left_col.addWidget(dict_to_card("Liên hệ", lien))
        left_col.addStretch()
        
        main_lay.addLayout(left_col, 1)
        
        lay.addLayout(main_lay)
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

# ══════════════════════════════════════════════════════════════════════════════
class BookDetailPage(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._current_book = None
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: #F8FAFC;")
        self.main_lay = QVBoxLayout(self.container)
        self.main_lay.setContentsMargins(40, 30, 40, 30)
        self.main_lay.setSpacing(20)

        scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def load_book(self, book):
        self._current_book = book
        # Clear
        while self.main_lay.count():
            item = self.main_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        # Reload from DB for fresh data
        try:
            from core.services.book_service import get_book_by_id
            fresh = get_book_by_id(book.get("BookID", ""))
            if fresh:
                book = fresh
                self._current_book = book
        except Exception:
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
                    font-size: 12px;
                    border: none;
                    padding: 0;
                    text-align: left;
                }}
                QPushButton:hover {{ text-decoration: underline; }}
            """)
            if action:
                lbl.clicked.connect(action)
            bread.addWidget(lbl)
        bread.addStretch()
        self.main_lay.addLayout(bread)

        # ── Main content card ─────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLOR_BORDER};
                border-radius: 16px;
            }}
        """)
        _shadow(card, 20, 5, 30)

        card_lay = QHBoxLayout(card)
        card_lay.setContentsMargins(32, 32, 32, 32)
        card_lay.setSpacing(32)

        # Left: Icon
        icon_container = QWidget()
        icon_container.setFixedSize(200, 200)
        icon_container.setStyleSheet(f"""
            background: {cat_info['bg']};
            border-radius: 20px;
        """)
        ic_lay = QVBoxLayout(icon_container)
        ic_lay.setAlignment(Qt.AlignCenter)
        icon_lbl = QLabel(cat_info["icon"])
        icon_lbl.setFont(QFont(FONT_FAMILY, 60))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("border: none; background: transparent;")
        ic_lay.addWidget(icon_lbl)
        card_lay.addWidget(icon_container)

        # Right: Info
        right = QVBoxLayout()
        right.setSpacing(10)

        # Badge row
        badge_row = QHBoxLayout()
        avail_badge = QLabel(f"  CÒN {available}/{quantity} SÁCH  ")
        avail_color = "#059669" if available > 0 else "#E11D48"
        avail_bg = "#ECFDF5" if available > 0 else "#FFF1F2"
        avail_badge.setStyleSheet(f"""
            background: {avail_bg};
            color: {avail_color};
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 12px;
            border: none;
        """)
        badge_row.addWidget(avail_badge)

        cat_badge = QLabel(f"  {book.get('Category', 'Khác')}  ")
        cat_badge.setStyleSheet(f"""
            background: {cat_info['bg']};
            color: {cat_info['fg']};
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 12px;
            border: none;
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

        # Author
        author = QLabel(f"✍️ {book.get('Author', '')}")
        author.setFont(QFont(FONT_FAMILY, 11))
        author.setStyleSheet(f"color: {COLOR_TEXT_MID}; border: none;")
        right.addWidget(author)

        right.addSpacing(10)

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
            info_card.setStyleSheet(f"""
                QFrame {{
                    background: {COLOR_PRIMARY_BG};
                    border-radius: 8px;
                    border: none;
                }}
            """)
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

        right.addSpacing(10)

        # Tóm tắt
        summary = QLabel("📄 Đây là tài liệu thuộc kho sách thư viện đại học. "
                         "Liên hệ thủ thư hoặc đăng ký mượn trực tuyến.")
        summary.setWordWrap(True)
        summary.setStyleSheet(f"""
            color: {COLOR_TEXT_MID};
            font-size: 12px;
            background: #FAFBFF;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
        """)
        right.addWidget(summary)

        right.addSpacing(10)

        # Button
        btn_borrow = QPushButton("📖 Đăng ký mượn sách")
        btn_borrow.setFixedHeight(46)
        btn_borrow.setCursor(Qt.PointingHandCursor)
        btn_borrow.setEnabled(available > 0)
        if available > 0:
            btn_borrow.setStyleSheet(f"""
                QPushButton {{
                    background: {NAV_BG};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background: {NAV_BG_DARK}; }}
            """)
        else:
            btn_borrow.setStyleSheet(f"""
                QPushButton {{
                    background: #CBD5E0;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
        btn_borrow.clicked.connect(self._borrow)
        right.addWidget(btn_borrow)

        right.addStretch()
        card_lay.addLayout(right, 1)
        self.main_lay.addWidget(card)
        self.main_lay.addStretch()

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
                self.load_book(self._current_book)  # Refresh
            else:
                QMessageBox.warning(self, "Không thể mượn", msg)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())


# ══════════════════════════════════════════════════════════════════════════════
#  4. STUDENT DASHBOARD

# ══════════════════════════════════════════════════════════════════════════════
#  6. STUDENT DASHBOARD (TRANG CÁ NHÂN)
# ══════════════════════════════════════════════════════════════════════════════
class StudentDashboard(QWidget):
    def __init__(self, portal, parent=None):
        super().__init__(parent)
        self.portal = portal
        self._build()

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

        student = self.portal.current_student
        name = student.get("Name", "Sinh viên")
        sid = student.get("StudentID", "")

        # ── Header ────────────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background: #1A2B4C;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(40, 30, 40, 30)
        
        row = QHBoxLayout()
        v_left = QVBoxLayout()
        v_left.setSpacing(2)
        
        h1 = QLabel(f"Xin chào, <span style='font-style:italic; color:#F5C05B;'>{name}</span>")
        h1.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        h1.setStyleSheet("color: white;")
        v_left.addWidget(h1)
        
        lbl_info = QLabel(f"MSSV: {sid} • Thẻ #{sid}-TH • Còn hạn đến 31/08/2026")
        lbl_info.setStyleSheet("color: #94A3B8; font-size: 11px;")
        v_left.addWidget(lbl_info)
        
        row.addLayout(v_left)
        row.addStretch()
        
        search_row = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm tài liệu...")
        self.inp_search.setFixedHeight(36)
        self.inp_search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px;
                padding: 0 16px;
                color: white;
            }
        """)
        self.inp_search.setFixedWidth(250)
        self.inp_search.returnPressed.connect(self._do_search)
        
        self.btn_search = QPushButton("Tìm kiếm")
        self.btn_search.setFixedHeight(36)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background: #F5C05B;
                color: #2D3748;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-weight: bold;
            }
        """)
        self.btn_search.clicked.connect(self._do_search)
        
        search_row.addWidget(self.inp_search)
        search_row.addWidget(self.btn_search)
        
        row.addLayout(search_row)
        h_lay.addLayout(row)
        lay.addWidget(header)

        # ── Stat Cards ────────────────────────────────────────────────────
        stats_ctn = QWidget()
        stats_ctn.setStyleSheet("background: #F8FAFC;")
        slay = QHBoxLayout(stats_ctn)
        slay.setContentsMargins(40, 30, 40, 10)
        slay.setSpacing(20)

        stats = [
            ("Đang mượn", "0", "/ 6 quyển tối đa", "#1A2B4C"),
            ("Sắp hết hạn", "0", "trong 2 ngày tới", "#D97706"),
            ("Phí phạt", "0", "cần thanh toán", "#DC2626")
        ]
        
        self.stat_cards = {}
        for title, val, sub, color in stats:
            c = QFrame()
            c.setStyleSheet("""
                QFrame {
                    background: #F4F2EB;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                }
            """)
            cl = QVBoxLayout(c)
            cl.setContentsMargins(20, 20, 20, 20)
            cl.setSpacing(10)
            
            tl = QLabel(title)
            tl.setStyleSheet("color: #718096; font-size: 11px; border:none;")
            cl.addWidget(tl)
            
            val_l = QLabel(val)
            val_l.setFont(QFont(FONT_FAMILY, 16, QFont.Bold))
            val_l.setStyleSheet(f"color: {color}; border:none; margin: -5px 0;")
            cl.addWidget(val_l)
            
            sub_l = QLabel(sub)
            sub_l.setStyleSheet("color: #A0AEC0; font-size: 10px; border:none;")
            cl.addWidget(sub_l)
            slay.addWidget(c)
            
            self.stat_cards[title] = val_l
            
        lay.addWidget(stats_ctn)

        # ── 2 Columns Content ────────────────────────────────────────────────
        main_lay = QHBoxLayout()
        main_lay.setContentsMargins(40, 20, 40, 40)
        main_lay.setSpacing(30)

        # -- Left Column (Sách đang mượn)
        left = QVBoxLayout()
        
        sach = QFrame()
        sach.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        sach_lay = QVBoxLayout(sach)
        sach_lay.setContentsMargins(20, 20, 20, 20)
        sach_lay.setSpacing(0)
        
        lt = QLabel("Sách đang mượn")
        lt.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        lt.setStyleSheet("color: #1A2B4C; border:none;")
        sach_lay.addWidget(lt)
        sach_lay.addSpacing(20)
        
        bks = [
            ("Giải tích 1 — Nguyễn Đình Trí", "Giáo trình • CNTT", "2 ngày", "#FEF3C7", "#D97706"),
            ("Computer Networks — Tanenbaum", "Tham khảo • Tiếng Anh", "12 ngày", "#ECFDF5", "#059669"),
            ("Design Patterns — GoF", "Tham khảo • Tiếng Anh", "14 ngày", "#ECFDF5", "#059669"),
            ("Xác suất thống kê — Đào Hữu Hồ", "Giáo trình", "18 ngày", "#ECFDF5", "#059669")
        ]
        
        self.borrowed_container = QVBoxLayout()
        self.borrowed_container.setSpacing(0)
        for ti, su, ba, bbg, bfg in bks:
            r = QHBoxLayout()
            r.setContentsMargins(0,10,0,10)
            
            vl = QVBoxLayout()
            vl.setSpacing(2)
            tt = QLabel(ti)
            tt.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
            tt.setStyleSheet("color: #2D3748; border:none;")
            vl.addWidget(tt)
            
            sl = QLabel(su)
            sl.setStyleSheet("color: #A0AEC0; font-size: 10px; border:none;")
            vl.addWidget(sl)
            r.addLayout(vl)
            r.addStretch()
            
            bl = QLabel(ba)
            bl.setFixedSize(60, 24)
            bl.setAlignment(Qt.AlignCenter)
            bl.setStyleSheet(f"background: {bbg}; color: {bfg}; font-size: 10px; border-radius: 12px; font-weight:bold; border:none;")
            r.addWidget(bl)
            
            fr = QFrame()
            fr.setStyleSheet("border-bottom: 1px solid #E2E8F0;")
            fr.setLayout(r)
            self.borrowed_container.addWidget(fr)
            
        sach_lay.addLayout(self.borrowed_container)
        sach_lay.addSpacing(20)
        
        acts = QHBoxLayout()
        gh = QPushButton("Gia hạn tất cả")
        gh.setFixedSize(100, 32)
        gh.setCursor(Qt.PointingHandCursor)
        gh.setStyleSheet("background: white; color: #4A5568; border: 1px solid #E2E8F0; border-radius: 16px; font-size: 11px;")
        gh.clicked.connect(self._extend_all)
        
        ls = QPushButton("Lịch sử mượn trả →")
        ls.setCursor(Qt.PointingHandCursor)
        ls.setStyleSheet("background: transparent; color: #D97706; font-size: 11px; border:none;")
        ls.clicked.connect(self._show_history)
        
        acts.addWidget(gh)
        acts.addWidget(ls)
        acts.addStretch()
        
        sach_lay.addLayout(acts)
        left.addWidget(sach)
        left.addStretch()
        main_lay.addLayout(left, 5)
        
        # -- Right Column (Gợi ý & Quick Links)
        right = QVBoxLayout()
        right.setSpacing(20)
        
        # Gợi ý
        gy = QFrame()
        gy.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        gl = QVBoxLayout(gy)
        gl.setContentsMargins(20, 20, 20, 20)
        gl.setSpacing(0)
        
        glt = QLabel("Gợi ý cho bạn")
        glt.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        glt.setStyleSheet("color: #1A2B4C; border:none;")
        gl.addWidget(glt)
        gl.addSpacing(15)
        
        recs = [
            ("Clean Code — Robert C. Martin", "CNTT • Tham khảo"),
            ("Introduction to Algorithms", "CLRS • Giáo trình"),
            ("The Pragmatic Programmer", "Hunt & Thomas • Tham khảo")
        ]
        
        for ti, su in recs:
            r = QHBoxLayout()
            r.setContentsMargins(0, 10, 0, 10)
            vl = QVBoxLayout()
            vl.setSpacing(2)
            l1 = QLabel(ti)
            l1.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
            l1.setStyleSheet("color: #2D3748; border:none;")
            vl.addWidget(l1)
            l2 = QLabel(su)
            l2.setStyleSheet("color: #718096; font-size: 10px; border:none;")
            vl.addWidget(l2)
            r.addLayout(vl)
            
            r.addStretch()
            
            fr = ClickableFrame()
            fr.setStyleSheet("QFrame { border-bottom: 1px solid #E2E8F0; } QFrame:hover { background: #F8FAFC; }")
            fr.setCursor(Qt.PointingHandCursor)
            fr.setLayout(r)
            # Search part before the dash if present
            search_title = ti.split(" — ")[0]
            fr.clicked.connect(lambda _=False, t=search_title: self._do_suggest_search(t))
            gl.addWidget(fr)
            
        right.addWidget(gy)
        
        # Truy cập nhanh
        tc = QFrame()
        tc.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
        tcl = QVBoxLayout(tc)
        tcl.setContentsMargins(20, 20, 20, 20)
        
        tct = QLabel("Truy cập nhanh")
        tct.setStyleSheet("color: #718096; font-size: 12px; border:none;")
        tcl.addWidget(tct)
        tcl.addSpacing(10)
        
        qls = ["IEEE Xplore", "Luận văn ĐH Công nghệ Đông Á", "Gia hạn sách online"]
        for q in qls:
            r = QHBoxLayout()
            l1 = QLabel(q)
            l1.setStyleSheet("border:none; font-size: 11px;")
            l2 = QLabel("→")
            l2.setStyleSheet("border:none; color: #D97706; font-size: 11px;")
            r.addWidget(l1)
            r.addStretch()
            r.addWidget(l2)
            
            fr = ClickableFrame()
            fr.setStyleSheet("QFrame { border-bottom: 1px solid #E2E8F0; } QFrame:hover { background: #F8FAFC; }")
            fr.setCursor(Qt.PointingHandCursor)
            fr.clicked.connect(lambda _=False, txt=q: self._quick_link_action(txt))
            fr.setLayout(r)
            tcl.addWidget(fr)
            
        right.addWidget(tc)
        right.addStretch()
        main_lay.addLayout(right, 4)

        lay.addLayout(main_lay)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _do_search(self):
        kw = self.inp_search.text().strip()
        self._do_suggest_search(kw)
            
    def _do_suggest_search(self, kw):
        if not kw: return
        if hasattr(self.portal, 'explore_page'):
            self.portal.explore_page.set_keyword(kw)
            self.portal.show_page(1)
            
    def _extend_all(self):
        QMessageBox.information(self, "Gia hạn thành công", "Đã gửi yêu cầu gia hạn cho tất cả sách đang mượn. Vui lòng chờ thủ thư phê duyệt.")
        
    def _show_history(self):
        QMessageBox.information(self, "Lịch sử", "Tính năng xem chi tiết lịch sử mượn trả đang được cập nhật.")
        
    def _reserve_book(self, title):
        QMessageBox.information(self, "Đặt trước", f"Đã đặt chỗ thành công cuốn '{title}'. Vui lòng đến nhận sách trong vòng 24 giờ.")

    def _quick_link_action(self, txt):
        if "IEEE" in txt:
            QDesktopServices.openUrl(QUrl("https://ieeexplore.ieee.org/"))
        elif "Luận văn" in txt:
            if hasattr(self.portal, 'explore_page'):
                self.portal.explore_page.set_keyword("Luận văn")
                self.portal.show_page(1)
        elif "Đặt phòng" in txt:
            QMessageBox.information(self, "Dịch vụ", "Phòng học nhóm\n\nVui lòng liên hệ trực tiếp tại quầy thư viện để đăng ký.")
        elif "Gia hạn" in txt:
            self._extend_all()

    def refresh(self):
        student_id = self.portal.current_student.get("StudentID", "")
        # Dummy update stats based on real layout
        try:
            from core.services.student_service import get_student_stats
            stats = get_student_stats(student_id)
            self.stat_cards["Đang mượn"].setText(str(stats.get("borrowing", 0)))
            self.stat_cards["Chờ nhận"].setText("2") 
        except Exception as e:
            pass


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
        
        logo_text = QLabel("Đại học Công nghệ Đông Á")
        logo_text.setFont(QFont(FONT_FAMILY, 10, QFont.Bold))
        logo_text.setStyleSheet("color: white;")
        logo_text.setMinimumWidth(250)
        nav_lay.addWidget(logo_text)
        nav_lay.addSpacing(20)

        # Nav items
        self.nav_buttons = {}
        nav_items = [
            (0, "Trang chủ"),
            (1, "Tra cứu tài liệu"),
            (2, "CSDL trực tuyến"),
            (3, "Dịch vụ"),
            (4, "Giới thiệu"),
            (6, "Cá nhân") # Index 5 is BookDetailPage
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

        name = self.current_student.get("Name", "Sinh viên")
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "SV"

        avatar = AvatarLabel(initials, "rgba(255,255,255,0.25)", "white", 34, 17)
        nav_lay.addWidget(avatar)
        nav_lay.addSpacing(10)

        name_lbl = QLabel(name)
        name_lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
        name_lbl.setStyleSheet("color: rgba(255,255,255,0.95);")
        nav_lay.addWidget(name_lbl)
        nav_lay.addSpacing(16)

        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setFixedHeight(32)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: #F5C05B;
                color: #1A2B4C;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: #ECC94B;
            }
        """)
        btn_logout.clicked.connect(self._logout)
        nav_lay.addWidget(btn_logout)

        root.addWidget(navbar)

        # ── Stacked Pages ─────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #F8FAFC;")

        self.home_page = HomePage(self)
        self.explore_page = ExplorePage(self)
        self.csdl_page = CSDLPage(self)
        self.dv_page = DichVuPage(self)
        self.gt_page = GioiThieuPage(self)
        
        self.book_detail_page = BookDetailPage(self)
        self.dashboard_page = StudentDashboard(self)

        self.stack.addWidget(self.home_page)       # 0
        self.stack.addWidget(self.explore_page)    # 1
        self.stack.addWidget(self.csdl_page)       # 2
        self.stack.addWidget(self.dv_page)         # 3
        self.stack.addWidget(self.gt_page)         # 4
        self.stack.addWidget(self.book_detail_page)# 5
        self.stack.addWidget(self.dashboard_page)  # 6

        root.addWidget(self.stack, 1)

    def show_page(self, index):
        self.stack.setCurrentIndex(index)

        for idx, btn in self.nav_buttons.items():
            if idx == index:
                btn.setStyleSheet("""
                    QPushButton {
                        color: white;
                        font-weight: bold;
                        font-size: 13px;
                        border: none;
                        border-bottom: 3px solid #F5C05B;
                        padding: 0 16px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        color: rgba(255,255,255,0.7);
                        font-size: 13px;
                        border: none;
                        border-bottom: 3px solid transparent;
                        padding: 0 16px;
                    }
                    QPushButton:hover {
                        color: white;
                        border-bottom: 3px solid rgba(255,255,255,0.3);
                    }
                """)

        # Refresh
        if index == 0:
            self.home_page.refresh()
        elif index == 1:
            self.explore_page.refresh()
        elif index == 6:
            self.dashboard_page.refresh()

    def _logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất",
            "Bạn có chắc muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
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

