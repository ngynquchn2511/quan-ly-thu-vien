"""
styles.py - Toan bo style tap trung cho app
"""

PRIMARY      = "#5B8DEF"
PRIMARY_DARK = "#4070D4"
PRIMARY_LIGHT= "#EBF1FD"
WHITE        = "#FFFFFF"
BG           = "#F7F8FC"
BORDER       = "#E2E8F0"
TEXT_DARK    = "#1E293B"
TEXT_MID     = "#475569"
TEXT_MUTED   = "#94A3B8"
SUCCESS      = "#22C55E"
SUCCESS_BG   = "#F0FDF4"
WARNING      = "#F59E0B"
WARNING_BG   = "#FFFBEB"
DANGER       = "#EF4444"
DANGER_BG    = "#FEF2F2"
INFO_BG      = "#EBF1FD"

APP_STYLE = f"""
    QWidget {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
        color: {TEXT_DARK};
    }}
    QScrollBar:vertical {{
        background: {BG}; width: 8px; border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER}; border-radius: 4px; min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: #CBD5E1; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

SIDEBAR_BG = f"QWidget#Sidebar {{ background: {PRIMARY}; }}"

NAV_ITEM = f"""
    QPushButton {{
        background: transparent;
        color: rgba(255,255,255,0.75);
        border: none;
        border-left: 3px solid transparent;
        border-radius: 0;
        text-align: left;
        padding: 11px 18px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: rgba(255,255,255,0.12);
        color: white;
    }}
"""
NAV_ACTIVE = f"""
    QPushButton {{
        background: rgba(255,255,255,0.18);
        color: white;
        border: none;
        border-left: 3px solid white;
        border-radius: 0;
        text-align: left;
        padding: 11px 18px;
        font-size: 14px;
        font-weight: bold;
    }}
"""
TOPBAR = f"QWidget#Topbar {{ background: {WHITE}; border-bottom: 1px solid {BORDER}; }}"
CONTENT_BG = f"QWidget#Content {{ background: {BG}; }}"

BTN_PRIMARY = f"""
    QPushButton {{
        background: {PRIMARY}; color: white; border: none;
        border-radius: 8px; padding: 9px 20px; font-weight: 600;
    }}
    QPushButton:hover {{ background: {PRIMARY_DARK}; }}
    QPushButton:pressed {{ background: #3560C4; }}
    QPushButton:disabled {{ background: #CBD5E1; color: #94A3B8; }}
"""
BTN_OUTLINE = f"""
    QPushButton {{
        background: {WHITE}; color: {TEXT_MID};
        border: 1px solid {BORDER}; border-radius: 8px; padding: 9px 20px;
    }}
    QPushButton:hover {{ background: {PRIMARY_LIGHT}; color: {PRIMARY}; border-color: {PRIMARY}; }}
"""
BTN_DANGER = f"""
    QPushButton {{
        background: {WHITE}; color: {DANGER};
        border: 1px solid #FECACA; border-radius: 8px; padding: 9px 20px;
    }}
    QPushButton:hover {{ background: {DANGER_BG}; border-color: {DANGER}; }}
"""
BTN_SMALL = f"""
    QPushButton {{
        background: {WHITE}; color: {TEXT_MID};
        border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 12px;
    }}
    QPushButton:hover {{ background: {PRIMARY_LIGHT}; color: {PRIMARY}; border-color: {PRIMARY}; }}
"""
BTN_SMALL_DANGER = f"""
    QPushButton {{
        background: {WHITE}; color: {DANGER};
        border: 1px solid #FECACA; border-radius: 6px; padding: 4px 12px;
    }}
    QPushButton:hover {{ background: {DANGER_BG}; }}
"""

INPUT = f"""
    QLineEdit, QDateEdit {{
        background: {WHITE}; border: 1px solid {BORDER};
        border-radius: 8px; padding: 9px 13px; color: {TEXT_DARK};
    }}
    QLineEdit:focus, QDateEdit:focus {{
        border: 2px solid {PRIMARY}; padding: 8px 12px;
    }}
    QLineEdit:hover, QDateEdit:hover {{ border-color: #93C5FD; }}
"""
COMBO = f"""
    QComboBox {{
        background: {WHITE}; border: 1px solid {BORDER};
        border-radius: 8px; padding: 9px 13px; color: {TEXT_DARK};
    }}
    QComboBox:focus {{ border: 2px solid {PRIMARY}; padding: 8px 12px; }}
    QComboBox:hover {{ border-color: #93C5FD; }}
    QComboBox::drop-down {{ border: none; width: 28px; border-left: 1px solid {BORDER}; }}
    QComboBox QAbstractItemView {{
        background: {WHITE}; border: 1px solid {BORDER}; border-radius: 8px;
        selection-background-color: {PRIMARY_LIGHT}; selection-color: {PRIMARY}; padding: 4px;
    }}
"""

CARD = f"""
    QFrame {{
        background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px;
    }}
"""
CARD_FLAT = f"""
    QFrame {{
        background: {WHITE}; border: 1px solid {BORDER}; border-radius: 8px;
    }}
"""
INFO_BANNER = f"""
    QFrame {{
        background: {INFO_BG}; border: 1px solid #BFDBFE; border-radius: 8px;
    }}
"""

# ── TABLE — hover doi mau ca dong ────────────────────────────────────────────
TABLE = f"""
    QTableWidget {{
        background: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 10px;
        gridline-color: transparent;
        outline: none;
        color: {TEXT_DARK};
    }}
    QTableWidget::item {{
        padding: 0px 14px;
        border-bottom: 1px solid {BORDER};
        border-right: none;
        background: transparent;
    }}
    QTableWidget::item:hover {{
        background: {PRIMARY_LIGHT};
    }}
    QTableWidget::item:selected {{
        background: #DBEAFE;
        color: {PRIMARY_DARK};
    }}
    QHeaderView {{
        background: {WHITE};
    }}
    QHeaderView::section {{
        background: {BG};
        color: {TEXT_MID};
        font-weight: 600;
        font-size: 13px;
        padding: 12px 14px;
        border: none;
        border-bottom: 2px solid {BORDER};
        border-right: 1px solid {BORDER};
    }}
    QHeaderView::section:last {{
        border-right: none;
    }}
"""

DIALOG_BG = f"QDialog {{ background: {WHITE}; }}"

BADGE_SUCCESS = (SUCCESS_BG, "#166534")
BADGE_WARNING = (WARNING_BG, "#92400E")
BADGE_DANGER  = (DANGER_BG,  "#991B1B")
BADGE_INFO    = (INFO_BG,    PRIMARY_DARK)
BADGE_NEUTRAL = ("#F1F5F9",  TEXT_MID)

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt


def make_badge(text, bg, fg, min_width=80):
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setMinimumWidth(min_width)
    lbl.setFixedHeight(26)
    lbl.setStyleSheet(
        f"background: {bg}; color: {fg}; border-radius: 13px;"
        f"padding: 2px 12px; font-weight: 600; border: none; font-size: 13px;"
    )
    return lbl


def badge_widget(text, bg, fg, min_width=80):
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(8, 4, 8, 4)
    l.addWidget(make_badge(text, bg, fg, min_width))
    return w


def field_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {TEXT_MID}; font-weight: 600; font-size: 13px; border: none;"
    )
    return lbl


def section_divider():
    div = QFrame()
    div.setFrameShape(QFrame.HLine)
    div.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
    return div

# ── Hover helper cho table ────────────────────────────────────────────────────
def setup_table_hover(table):
    """
    Goi ham nay sau khi tao QTableWidget de co hover doi mau ca dong.
    Yeu cau: import trong file GUI.
    """
    from PyQt5.QtCore import Qt
    table.setMouseTracking(True)
    table.setSelectionBehavior(table.SelectRows)
    table._hovered_row = -1

    def on_cell_entered(row, col):
        if table._hovered_row == row:
            return
        # Reset dong cu
        if table._hovered_row >= 0:
            _set_row_bg(table, table._hovered_row, "")
        table._hovered_row = row
        _set_row_bg(table, row, PRIMARY_LIGHT)

    def on_leave(event):
        if table._hovered_row >= 0:
            _set_row_bg(table, table._hovered_row, "")
        table._hovered_row = -1

    table.cellEntered.connect(on_cell_entered)
    table.leaveEvent = on_leave


    def _set_row_bg(table, row, color):
        from PyQt5.QtGui import QColor
        from PyQt5.QtWidgets import QTableWidgetItem
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                if color:
                    item.setBackground(QColor(color))
                else:
                    item.setBackground(QColor(0, 0, 0, 0))