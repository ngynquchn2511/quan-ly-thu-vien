import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QComboBox, QSpinBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from database.db import get_connection
import core.styles as styles
from datetime import datetime, timedelta


MSG_STYLE = """
    QMessageBox { background: #F7F8FC; }
    QLabel { color: #1E293B; font-size: 14px; background: transparent; }
    QPushButton {
        background: white; color: #1E293B;
        border: 1px solid #E2E8F0; border-radius: 6px;
        padding: 8px 24px; min-width: 90px; font-size: 13px;
    }
    QPushButton:hover { background: #EBF1FD; color: #5B8DEF; border-color: #5B8DEF; }
"""


def show_msg(parent, title, text):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title); msg.setText(text)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.button(QMessageBox.Ok).setText("Đóng")
    msg.setStyleSheet(MSG_STYLE); msg.exec_()


# ── Bieu do thanh ngang ───────────────────────────────────────────────────────
class BarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data   = []   # list of (label, value)
        self.title  = ""
        self.color  = QColor(styles.PRIMARY)
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_data(self, data, title="", color=None):
        self.data  = data
        self.title = title
        if color: self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        if not self.data:
            p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
            p.setPen(QColor(styles.TEXT_MUTED))
            p.setFont(QFont("Segoe UI", 12))
            p.drawText(self.rect(), Qt.AlignCenter, "Chưa có dữ liệu")
            return

        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 60, 20, 56, 64

        # Title
        if self.title:
            p.setPen(QColor(styles.TEXT_DARK))
            p.setFont(QFont("Segoe UI", 12, QFont.Bold))
            p.drawText(0, 8, W, 24, Qt.AlignCenter, self.title)

        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b
        # Ho tro ca 2 kieu: (label, value) va (name, date, value)
        if self.data and len(self.data[0]) == 3:
            values   = [d[2] for d in self.data]
            labels1  = [d[0] for d in self.data]  # Thu
            labels2  = [d[1] for d in self.data]  # Ngay
        else:
            values   = [d[1] for d in self.data]
            labels1  = [d[0] for d in self.data]
            labels2  = []

        max_val = max(values) if values else 1
        n = len(self.data)
        bar_w = max(8, int(chart_w / n * 0.6))
        gap   = chart_w / n

        # Grid lines
        p.setPen(QPen(QColor(styles.BORDER), 0.5))
        for i in range(5):
            y = pad_t + int(chart_h * i / 4)
            p.drawLine(pad_l, y, W - pad_r, y)
            val = int(max_val * (4 - i) / 4)
            p.setPen(QColor(styles.TEXT_MUTED))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(0, y - 8, pad_l - 4, 16, Qt.AlignRight | Qt.AlignVCenter, str(val))
            p.setPen(QPen(QColor(styles.BORDER), 0.5))

        # Bars
        for i, value in enumerate(values):
            x = pad_l + int(i * gap + gap / 2 - bar_w / 2)
            bar_h = int(chart_h * value / max_val) if max_val > 0 else 0
            y = pad_t + chart_h - bar_h

            # Bar
            p.setBrush(QBrush(self.color))
            p.setPen(Qt.NoPen)
            if bar_h > 0:
                p.drawRoundedRect(x, y, bar_w, bar_h, 4, 4)

            # Value on top
            if value > 0:
                p.setPen(QColor(styles.TEXT_DARK))
                p.setFont(QFont("Segoe UI", 9, QFont.Bold))
                p.drawText(x - 10, y - 22, bar_w + 20, 18,
                           Qt.AlignCenter, str(value))

            # Label dong 1 (ten thu hoac ten thang)
            p.setPen(QColor(styles.TEXT_MID))
            p.setFont(QFont("Segoe UI", 9))
            lbl1 = labels1[i] if len(labels1[i]) <= 6 else labels1[i][:5]
            p.drawText(x - 10, H - pad_b + 4, bar_w + 20, 18,
                       Qt.AlignCenter, lbl1)

            # Label dong 2 (ngay thang) neu co
            if labels2:
                p.setFont(QFont("Segoe UI", 8))
                p.setPen(QColor(styles.TEXT_MUTED))
                p.drawText(x - 10, H - pad_b + 22, bar_w + 20, 16,
                           Qt.AlignCenter, labels2[i])

        # Axis
        p.setPen(QPen(QColor(styles.BORDER), 1))
        p.drawLine(pad_l, pad_t, pad_l, pad_t + chart_h)
        p.drawLine(pad_l, pad_t + chart_h, W - pad_r, pad_t + chart_h)


# ── Bieu do duong cho muon/mat sach ───────────────────────────────────────────
class LineCompareChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels = []
        self.borrow_values = []
        self.lost_values = []
        self.title = ""
        self.sub_labels = []
        self.setMinimumHeight(340)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_series(self, labels, borrow_values, lost_values, title="", sub_labels=None):
        self.labels = labels or []
        self.borrow_values = borrow_values or []
        self.lost_values = lost_values or []
        self.title = title
        self.sub_labels = sub_labels or []
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 70, 30, 56, 76

        if self.title:
            p.setPen(QColor(styles.TEXT_DARK))
            p.setFont(QFont("Segoe UI", 12, QFont.Bold))
            p.drawText(0, 8, W, 24, Qt.AlignCenter, self.title)

        if not self.labels:
            p.setPen(QColor(styles.TEXT_MUTED))
            p.setFont(QFont("Segoe UI", 12))
            p.drawText(self.rect(), Qt.AlignCenter, "Chưa có dữ liệu")
            return

        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b
        max_val = max(self.borrow_values + self.lost_values + [1])

        p.setPen(QPen(QColor(styles.BORDER), 0.5))
        for i in range(5):
            y = pad_t + int(chart_h * i / 4)
            p.drawLine(pad_l, y, W - pad_r, y)
            val = int(max_val * (4 - i) / 4)
            p.setPen(QColor(styles.TEXT_MUTED))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(0, y - 8, pad_l - 6, 16, Qt.AlignRight | Qt.AlignVCenter, str(val))
            p.setPen(QPen(QColor(styles.BORDER), 0.5))

        n = len(self.labels)
        if n == 1:
            xs = [pad_l + chart_w // 2]
        else:
            gap = chart_w / max(1, n - 1)
            xs = [pad_l + int(i * gap) for i in range(n)]
        base_y = pad_t + chart_h

        def calc_points(values):
            return [
                (xs[i], pad_t + chart_h - int(chart_h * values[i] / max_val if max_val else 0))
                for i in range(n)
            ]

        borrow_points = calc_points(self.borrow_values)
        lost_points = calc_points(self.lost_values)
        green = QColor("#16A34A")
        blue = QColor("#2563EB")

        def draw_series(points, color, values):
            if not points:
                return
            p.setPen(QPen(color, 3))
            for i in range(len(points) - 1):
                p.drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            for i, (x, y) in enumerate(points):
                p.drawEllipse(x - 4, y - 4, 8, 8)
                if values[i] > 0:
                    p.setPen(QColor(styles.TEXT_DARK))
                    p.setFont(QFont("Segoe UI", 8, QFont.Bold))
                    p.drawText(x - 18, y - 20, 36, 14, Qt.AlignCenter, str(values[i]))
                    p.setPen(Qt.NoPen)

        draw_series(borrow_points, green, self.borrow_values)
        draw_series(lost_points, blue, self.lost_values)

        p.setPen(QPen(QColor(styles.BORDER), 1))
        p.drawLine(pad_l, pad_t, pad_l, base_y)
        p.drawLine(pad_l, base_y, W - pad_r, base_y)

        for i, x in enumerate(xs):
            p.setPen(QColor(styles.TEXT_MID))
            p.setFont(QFont("Segoe UI", 8 if n > 12 else 9))
            lbl = self.labels[i]
            if n > 20 and len(lbl) > 2:
                lbl = lbl[:2]
            p.drawText(x - 20, H - pad_b + 8, 40, 16, Qt.AlignCenter, lbl)
            if self.sub_labels:
                p.setPen(QColor(styles.TEXT_MUTED))
                p.setFont(QFont("Segoe UI", 8))
                p.drawText(x - 24, H - pad_b + 24, 48, 14, Qt.AlignCenter, self.sub_labels[i])

        legend_y = H - 28
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(green))
        p.drawRoundedRect(pad_l + 30, legend_y, 18, 8, 3, 3)
        p.setBrush(QBrush(blue))
        p.drawRoundedRect(pad_l + 180, legend_y, 18, 8, 3, 3)
        p.setPen(QColor(styles.TEXT_MID))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(pad_l + 56, legend_y - 6, 110, 20, Qt.AlignLeft | Qt.AlignVCenter, "Đang mượn")
        p.drawText(pad_l + 206, legend_y - 6, 90, 20, Qt.AlignLeft | Qt.AlignVCenter, "Mất sách")




def query_by_year(year):
    """So sach cho muon theo tung thang trong nam."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%m', BorrowDate) as month, COUNT(*) as cnt
        FROM Borrow
        WHERE strftime('%Y', BorrowDate) = ?
        GROUP BY month ORDER BY month
    """, (str(year),))
    rows = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()
    MONTHS = ["T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12"]
    return [(MONTHS[i], rows.get(f"{i+1:02d}", 0)) for i in range(12)]


def query_by_month(year, month):
    """So sach cho muon theo tung ngay trong thang."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%d', BorrowDate) as day, COUNT(*) as cnt
        FROM Borrow
        WHERE strftime('%Y', BorrowDate) = ?
          AND strftime('%m', BorrowDate) = ?
        GROUP BY day ORDER BY day
    """, (str(year), f"{month:02d}"))
    rows = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    return [(str(d), rows.get(f"{d:02d}", 0)) for d in range(1, days_in_month + 1)]


def query_by_week(year, week):
    """So sach cho muon theo tung ngay trong tuan."""
    conn = get_connection(); cur = conn.cursor()
    jan1 = datetime(year, 1, 1)
    start = jan1 + timedelta(weeks=week-1)
    start = start - timedelta(days=start.weekday())
    days = [(start + timedelta(days=i)) for i in range(7)]
    DAY_NAMES = ["T2","T3","T4","T5","T6","T7","CN"]
    result = []
    for i, d in enumerate(days):
        cur.execute(
            "SELECT COUNT(*) FROM Borrow WHERE BorrowDate = ?",
            (d.strftime("%Y-%m-%d"),))
        cnt = cur.fetchone()[0]
        # Tra ve tuple (ten_thu, ngay, so_luot) thay vi dung \n
        result.append((DAY_NAMES[i], d.strftime("%d/%m"), cnt))
    conn.close()
    return result


def query_all_time():
    """So sach cho muon theo tung nam."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y', BorrowDate) as year, COUNT(*) as cnt
        FROM Borrow
        WHERE BorrowDate IS NOT NULL
        GROUP BY year ORDER BY year
    """)
    rows = cur.fetchall(); conn.close()
    return [(r[0], r[1]) for r in rows] if rows else [("Chưa có", 0)]


def query_borrow_lost_by_year(year):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%m', BorrowDate) as period,
               SUM(CASE WHEN Status='Borrowing' THEN 1 ELSE 0 END) as borrowing_cnt,
               SUM(CASE WHEN Status='Lost' THEN 1 ELSE 0 END) as lost_cnt
        FROM Borrow
        WHERE strftime('%Y', BorrowDate)=?
        GROUP BY period ORDER BY period
    """, (str(year),))
    rows = {r[0]: (r[1] or 0, r[2] or 0) for r in cur.fetchall()}
    conn.close()
    labels = [f"T{i}" for i in range(1, 13)]
    borrow_values = [rows.get(f"{i:02d}", (0, 0))[0] for i in range(1, 13)]
    lost_values = [rows.get(f"{i:02d}", (0, 0))[1] for i in range(1, 13)]
    return labels, borrow_values, lost_values, []


def query_borrow_lost_by_month(year, month):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%d', BorrowDate) as period,
               SUM(CASE WHEN Status='Borrowing' THEN 1 ELSE 0 END) as borrowing_cnt,
               SUM(CASE WHEN Status='Lost' THEN 1 ELSE 0 END) as lost_cnt
        FROM Borrow
        WHERE strftime('%Y', BorrowDate)=?
          AND strftime('%m', BorrowDate)=?
        GROUP BY period ORDER BY period
    """, (str(year), f"{month:02d}"))
    rows = {r[0]: (r[1] or 0, r[2] or 0) for r in cur.fetchall()}
    conn.close()
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    labels = [str(d) for d in range(1, days_in_month + 1)]
    borrow_values = [rows.get(f"{d:02d}", (0, 0))[0] for d in range(1, days_in_month + 1)]
    lost_values = [rows.get(f"{d:02d}", (0, 0))[1] for d in range(1, days_in_month + 1)]
    return labels, borrow_values, lost_values, []


def query_borrow_lost_by_week(year, week):
    conn = get_connection(); cur = conn.cursor()
    jan1 = datetime(year, 1, 1)
    start = jan1 + timedelta(weeks=week-1)
    start = start - timedelta(days=start.weekday())
    days = [(start + timedelta(days=i)) for i in range(7)]
    day_names = ["T2","T3","T4","T5","T6","T7","CN"]
    labels, sub_labels, borrow_values, lost_values = [], [], [], []
    for i, d in enumerate(days):
        date_str = d.strftime("%Y-%m-%d")
        cur.execute("""
            SELECT
                SUM(CASE WHEN Status='Borrowing' THEN 1 ELSE 0 END),
                SUM(CASE WHEN Status='Lost' THEN 1 ELSE 0 END)
            FROM Borrow
            WHERE BorrowDate = ?
        """, (date_str,))
        row = cur.fetchone()
        labels.append(day_names[i])
        sub_labels.append(d.strftime("%d/%m"))
        borrow_values.append((row[0] or 0) if row else 0)
        lost_values.append((row[1] or 0) if row else 0)
    conn.close()
    return labels, borrow_values, lost_values, sub_labels


def query_borrow_lost_all_time():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y', BorrowDate) as period,
               SUM(CASE WHEN Status='Borrowing' THEN 1 ELSE 0 END) as borrowing_cnt,
               SUM(CASE WHEN Status='Lost' THEN 1 ELSE 0 END) as lost_cnt
        FROM Borrow
        WHERE BorrowDate IS NOT NULL
        GROUP BY period ORDER BY period
    """)
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return ["Chưa có"], [0], [0], []
    labels = [r[0] for r in rows]
    borrow_values = [r[1] or 0 for r in rows]
    lost_values = [r[2] or 0 for r in rows]
    return labels, borrow_values, lost_values, []


# ── Chart Panel ───────────────────────────────────────────────────────────────
class ChartPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.CARD)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        # Title
        title_lbl = QLabel("Biểu đồ thống kê mượn sách")
        title_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_lbl.setStyleSheet(f"color:{styles.TEXT_DARK}; border:none;")
        lay.addWidget(title_lbl)
        lay.addWidget(styles.section_divider())

        # Controls
        ctrl = QHBoxLayout(); ctrl.setSpacing(10)

        # Chon kieu
        ctrl.addWidget(styles.field_label("Xem theo:"))
        self.cmb_type = QComboBox()
        self.cmb_type.setStyleSheet(styles.COMBO)
        self.cmb_type.setFixedHeight(36); self.cmb_type.setFixedWidth(130)
        self.cmb_type.addItems(["Năm", "Tháng", "Tuần", "Tất cả thời gian"])
        self.cmb_type.currentTextChanged.connect(self._on_type_change)
        ctrl.addWidget(self.cmb_type)

        # Nam
        ctrl.addWidget(styles.field_label("Năm:"))
        self.spn_year = QSpinBox()
        self.spn_year.setStyleSheet(styles.INPUT)
        self.spn_year.setFixedHeight(36); self.spn_year.setFixedWidth(80)
        self.spn_year.setRange(2000, 2100)
        self.spn_year.setValue(datetime.now().year)
        ctrl.addWidget(self.spn_year)

        # Thang
        self.lbl_month = styles.field_label("Tháng:")
        ctrl.addWidget(self.lbl_month)
        self.cmb_month = QComboBox()
        self.cmb_month.setStyleSheet(styles.COMBO)
        self.cmb_month.setFixedHeight(36); self.cmb_month.setFixedWidth(80)
        for i in range(1, 13):
            self.cmb_month.addItem(f"T{i}", i)
        self.cmb_month.setCurrentIndex(datetime.now().month - 1)
        ctrl.addWidget(self.cmb_month)
        self.lbl_month.hide(); self.cmb_month.hide()

        # Tuan
        self.lbl_week = styles.field_label("Tuần:")
        ctrl.addWidget(self.lbl_week)
        self.spn_week = QSpinBox()
        self.spn_week.setStyleSheet(styles.INPUT)
        self.spn_week.setFixedHeight(36); self.spn_week.setFixedWidth(70)
        self.spn_week.setRange(1, 53)
        self.spn_week.setValue(datetime.now().isocalendar()[1])
        ctrl.addWidget(self.spn_week)
        self.lbl_week.hide(); self.spn_week.hide()

        # Nut xem
        btn_view = QPushButton("Xem biểu đồ")
        btn_view.setStyleSheet(styles.BTN_PRIMARY)
        btn_view.setFixedHeight(36)
        btn_view.clicked.connect(self.load_chart)
        ctrl.addStretch()
        ctrl.addWidget(btn_view)
        lay.addLayout(ctrl)

        # Thong ke nhanh
        self.lbl_summary = QLabel()
        self.lbl_summary.setStyleSheet(
            f"color:{styles.TEXT_MID}; font-size:13px; border:none;")
        lay.addWidget(self.lbl_summary)

        # Chart
        self.chart = BarChart()
        self.chart.setMinimumHeight(400)
        lay.addWidget(self.chart)

        self.borrow_lost_chart = LineCompareChart()
        self.borrow_lost_chart.hide()
        lay.addWidget(self.borrow_lost_chart)

        self.mode = "borrow"
        self.external_loader = None

        # Load lan dau
        self.load_chart()

    def _on_type_change(self, t):
        is_month = t == "Tháng"
        is_week  = t == "Tuần"
        is_all   = t == "Tất cả thời gian"

        self.lbl_month.setVisible(is_month)
        self.cmb_month.setVisible(is_month)
        self.lbl_week.setVisible(is_week)
        self.spn_week.setVisible(is_week)
        self.spn_year.setVisible(not is_all)
        if self.external_loader:
            self.external_loader()
        else:
            self.chart.show()
            self.borrow_lost_chart.hide()
            self.load_chart()

    def load_chart(self):
        t     = self.cmb_type.currentText()
        year  = self.spn_year.value()
        month = self.cmb_month.currentData()
        week  = self.spn_week.value()

        try:
            if t == "Năm":
                data  = query_by_year(year)
                title = f"Số lượt mượn theo tháng — Năm {year}"
                color = styles.PRIMARY

            elif t == "Tháng":
                data  = query_by_month(year, month)
                title = f"Số lượt mượn theo ngày — Tháng {month}/{year}"
                color = "#1D9E75"

            elif t == "Tuần":
                data  = query_by_week(year, week)
                title = f"Số lượt mượn — Tuần {week}/{year}"
                color = "#BA7517"

            else:  # Tat ca
                data  = query_all_time()
                title = "Tổng số lượt mượn theo năm"
                color = "#534AB7"

            self.chart.show()
            self.borrow_lost_chart.hide()
            self.chart.set_data(data, title, color)

            if data and len(data[0]) == 3:
                total = sum(d[2] for d in data)
                max_v = max((d[2] for d in data), default=0)
                max_l = next((f"{d[0]} {d[1]}" for d in data if d[2]==max_v), "")
            else:
                total = sum(v for _, v in data)
                max_v = max((v for _, v in data), default=0)
                max_l = next((l for l, v in data if v == max_v), "")
            self.lbl_summary.setText(
                f"Tổng: {total} lượt mượn  •  Cao nhất: {max_l} ({max_v} lượt)")

        except Exception as e:
            print(f"[Chart] {e}")

    def trigger_refresh(self):
        if self.external_loader:
            self.external_loader()
        else:
            self.load_chart()


# ── Report Card ───────────────────────────────────────────────────────────────
class ReportCard(QFrame):
    def __init__(self, icon, title, desc, callback, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(110)
        self._normal = f"QFrame {{ background:{styles.WHITE}; border:1px solid {styles.BORDER}; border-radius:12px; }}"
        self._hover  = f"QFrame {{ background:{styles.PRIMARY_LIGHT}; border:2px solid {styles.PRIMARY}; border-radius:12px; }}"
        self.setStyleSheet(self._normal)
        lay = QVBoxLayout(self); lay.setContentsMargins(18,14,18,14); lay.setSpacing(8)
        top = QHBoxLayout()
        ic = QLabel(icon); ic.setFixedSize(38,38); ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"background:{styles.PRIMARY_LIGHT}; border-radius:10px; border:none; font-size:18px;")
        top.addWidget(ic); top.addStretch(); lay.addLayout(top)
        t = QLabel(title); t.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:600; border:none;")
        d = QLabel(desc);  d.setStyleSheet(f"color:{styles.TEXT_MUTED}; font-size:13px; border:none;")
        lay.addWidget(t); lay.addWidget(d)

    def mousePressEvent(self, e):
        if self.callback: self.callback()

    def enterEvent(self, e): self.setStyleSheet(self._hover)
    def leaveEvent(self, e): self.setStyleSheet(self._normal)


# ── Reports Window ────────────────────────────────────────────────────────────
class ReportsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._load_stats()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent; border:none;")
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(16)

        # 6 card chuc nang
        grid = QGridLayout(); grid.setSpacing(12)
        cards = [
            ("📄","Báo cáo mượn trả",    "Xuất Excel theo kỳ",          self._export_borrow),
            ("📊","Thống kê sách",        "Top sách mượn nhiều",         self._show_chart_and_top),
            ("📚","TK mượn & mất sách",  "Đang cho mượn và sách mất",   self._show_borrow_lost_stats),
            ("⚠", "Danh sách quá hạn",   "Kèm tiền phạt",               self._show_overdue),
            ("👤","Thống kê độc giả",     "Hoạt động theo tháng",        self._show_students),
            ("💰","Báo cáo tiền phạt",    "Tiền phạt thu được",          self._show_fines),
        ]
        for idx, (icon, title, desc, cb) in enumerate(cards):
            grid.addWidget(ReportCard(icon, title, desc, cb), idx // 3, idx % 3)
        lay.addLayout(grid)

        # Bieu do thong ke
        self.chart_panel = ChartPanel()
        lay.addWidget(self.chart_panel)

        # An bieu do mac dinh, chi hien khi bam nut thong ke
        self.chart_panel.hide()

        # Bieu do the loai (thanh ngang nho)
        panel = QFrame(); panel.setStyleSheet(styles.CARD)
        pl = QVBoxLayout(panel); pl.setContentsMargins(20,16,20,16); pl.setSpacing(12)
        ph = QLabel("Thống kê mượn sách theo thể loại")
        ph.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:600; border:none;")
        pl.addWidget(ph)
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background:{styles.BORDER}; max-height:1px; border:none;")
        pl.addWidget(div)
        self.bar_container = QVBoxLayout(); self.bar_container.setSpacing(10)
        pl.addLayout(self.bar_container)
        self.panel_category = panel
        self.panel_category.hide()
        lay.addWidget(self.panel_category)

        # Bang ket qua
        self.result_label = QLabel()
        self.result_label.setStyleSheet(f"color:{styles.TEXT_DARK}; font-weight:600; border:none;")
        self.result_label.hide()
        lay.addWidget(self.result_label)

        self.table = QTableWidget()
        self.table.setStyleSheet(styles.TABLE)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.hide()
        lay.addWidget(self.table)
        lay.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

    def _load_stats(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT bk.Category, COUNT(*) as cnt FROM Borrow b
                JOIN Books bk ON b.BookID=bk.BookID
                GROUP BY bk.Category ORDER BY cnt DESC LIMIT 8
            """)
            rows = cur.fetchall(); conn.close()
        except: rows = []

        while self.bar_container.count():
            item = self.bar_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not rows:
            lbl = QLabel("Chưa có dữ liệu.")
            lbl.setStyleSheet(f"color:{styles.TEXT_MUTED}; border:none;")
            self.bar_container.addWidget(lbl); return

        max_cnt = max(r[1] for r in rows) or 1
        for cat, cnt in rows:
            rw = QWidget(); rl = QHBoxLayout(rw)
            rl.setContentsMargins(0,0,0,0); rl.setSpacing(12)
            lbl_cat = QLabel(cat or "Khác")
            lbl_cat.setFixedWidth(110)
            lbl_cat.setStyleSheet(f"color:{styles.TEXT_MID}; border:none;")
            track = QFrame(); track.setFixedHeight(10)
            track.setStyleSheet(f"background:{styles.BG}; border-radius:5px; border:1px solid {styles.BORDER};")
            fill = QFrame(track); fill.setFixedHeight(10)
            fill.setStyleSheet(f"background:{styles.PRIMARY}; border-radius:5px; border:none;")
            fill.setFixedWidth(max(8, int(cnt/max_cnt*100*2.8)))
            lbl_cnt = QLabel(f"{cnt} lượt")
            lbl_cnt.setStyleSheet(f"color:{styles.TEXT_MID}; border:none;"); lbl_cnt.setFixedWidth(65)
            rl.addWidget(lbl_cat); rl.addWidget(track,1); rl.addWidget(lbl_cnt)
            self.bar_container.addWidget(rw)

    def _show_table(self, title, headers, rows):
        self.result_label.setText(title); self.result_label.show()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(0)
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(i, j, item)
            self.table.setRowHeight(i, 44)
        hdr = self.table.horizontalHeader()
        for c in range(len(headers)): hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        if headers: hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        total_h = len(rows) * 44 + 52
        self.table.setFixedHeight(total_h); self.table.show()

    def _hide_chart(self):
        self.chart_panel.hide()
        self.panel_category.hide()

    def _show_chart_and_top(self):
        self.chart_panel.external_loader = None
        self.chart_panel.show()
        self.chart_panel.load_chart()
        self.panel_category.show()
        self._load_stats()
        self._show_top_books()

    def _show_top_books(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT bk.Title, bk.Author, COUNT(*) as cnt FROM Borrow b
            JOIN Books bk ON b.BookID=bk.BookID
            GROUP BY b.BookID ORDER BY cnt DESC LIMIT 10
        """)
        rows = cur.fetchall(); conn.close()
        self._show_table("Top 10 sách được mượn nhiều nhất",
            ["Tên sách","Tác giả","Số lần mượn"], rows)

    def _show_overdue(self):
        self._hide_chart()
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT s.Name, s.StudentID, bk.Title, b.DueDate,
                   CAST(julianday('now')-julianday(b.DueDate) AS INTEGER) as days,
                   b.FineAmount
            FROM Borrow b JOIN Students s ON b.StudentID=s.StudentID
            JOIN Books bk ON b.BookID=bk.BookID
            WHERE b.Status='Overdue' ORDER BY b.DueDate ASC
        """)
        rows = cur.fetchall(); conn.close()
        data = [(r[0],r[1],r[2],r[3],f"{r[4]} ngày",f"{r[5]:,.0f}đ") for r in rows]
        self._show_table(f"Danh sách sách quá hạn ({len(data)} phiếu)",
            ["Họ tên","Mã SV","Tên sách","Hạn trả","Số ngày quá","Tiền phạt"], data)

    def _show_students(self):
        self._hide_chart()
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT s.Name, s.StudentID, s.Faculty, COUNT(b.BorrowID) as total
            FROM Students s LEFT JOIN Borrow b ON s.StudentID=b.StudentID
            GROUP BY s.StudentID ORDER BY total DESC
        """)
        rows = cur.fetchall(); conn.close()
        self._show_table("Thống kê mượn sách theo độc giả",
            ["Họ tên","Mã SV","Khoa","Tổng lượt mượn"], rows)

    def _show_fines(self):
        self._hide_chart()
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT s.Name, s.StudentID, b.DueDate, b.ReturnDate, b.FineAmount,
                   CASE b.FinePaid WHEN 1 THEN 'Đã nộp' ELSE 'Chưa nộp' END
            FROM Borrow b JOIN Students s ON b.StudentID=s.StudentID
            WHERE b.FineAmount > 0 ORDER BY b.FineAmount DESC
        """)
        rows = cur.fetchall(); conn.close()
        data = [(r[0],r[1],r[2],r[3] or "",f"{r[4]:,.0f}đ",r[5]) for r in rows]
        self._show_table(f"Báo cáo tiền phạt ({len(data)} phiếu)",
            ["Họ tên","Mã SV","Hạn trả","Ngày trả","Tiền phạt","Trạng thái"], data)

    def _show_borrow_lost_stats(self):
        t = self.chart_panel.cmb_type.currentText()
        year = self.chart_panel.spn_year.value()
        month = self.chart_panel.cmb_month.currentData()
        week = self.chart_panel.spn_week.value()

        if t == "Năm":
            labels, borrow_values, lost_values, sub_labels = query_borrow_lost_by_year(year)
            title = f"Sách đang mượn và mất sách theo tháng — Năm {year}"
        elif t == "Tháng":
            labels, borrow_values, lost_values, sub_labels = query_borrow_lost_by_month(year, month)
            title = f"Sách đang mượn và mất sách theo ngày — Tháng {month}/{year}"
        elif t == "Tuần":
            labels, borrow_values, lost_values, sub_labels = query_borrow_lost_by_week(year, week)
            title = f"Sách đang mượn và mất sách — Tuần {week}/{year}"
        else:
            labels, borrow_values, lost_values, sub_labels = query_borrow_lost_all_time()
            title = "Sách đang mượn và mất sách theo năm"

        total_borrowing = sum(borrow_values)
        total_lost = sum(lost_values)

        self.chart_panel.show()
        self.chart_panel.external_loader = self._show_borrow_lost_stats
        self.chart_panel.chart.hide()
        self.chart_panel.borrow_lost_chart.show()
        self.chart_panel.borrow_lost_chart.set_series(
            labels,
            borrow_values,
            lost_values,
            title,
            sub_labels
        )
        self.chart_panel.lbl_summary.setText(
            f"Tổng đang cho mượn: {total_borrowing}  •  Tổng mất sách: {total_lost}")
        self.panel_category.hide()

        data = [(labels[i], borrow_values[i], lost_values[i]) for i in range(len(labels))]
        self._show_table(
            f"Thống kê mượn và mất sách theo thời gian ({len(data)} mốc)",
            ["Thời gian", "Đang mượn", "Mất sách"],
            data
        )

    def _export_borrow(self):
        self._hide_chart()
        try:
            from reports.export_excel import export_borrow_report
            path, _ = QFileDialog.getSaveFileName(
                self,"Lưu file","bao_cao_muon_tra.csv","CSV (*.csv)")
            if path:
                export_borrow_report(path)
                show_msg(self,"Thành công",f"Đã xuất file:\n{path}")
        except ImportError:
            show_msg(self,"Thiếu thư viện","Vui lòng cài: pip install pandas openpyxl")
        except Exception as e:
            show_msg(self,"Lỗi",str(e))