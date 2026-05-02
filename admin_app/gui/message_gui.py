import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QListWidget, QListWidgetItem,
    QTextEdit, QSplitter, QSizePolicy, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
import core.styles as styles


class TimeDivider(QWidget):
    """Hien thi thoi gian phan cach giua cac nhom tin nhan."""
    def __init__(self, time_str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 8, 0, 8); lay.setSpacing(8)
        line1 = QFrame(); line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet(f"background: {styles.BORDER}; border: none;")
        lbl = QLabel(time_str)
        lbl.setStyleSheet(
            f"color: {styles.TEXT_MUTED}; font-size: 11px; border: none;"
            f"background: transparent; padding: 0 6px;")
        lbl.setFixedHeight(16)
        line2 = QFrame(); line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet(f"background: {styles.BORDER}; border: none;")
        lay.addWidget(line1, 1); lay.addWidget(lbl); lay.addWidget(line2, 1)


class BubbleWidget(QFrame):
    """Widget hien thi 1 tin nhan dang bubble."""
    def __init__(self, content, sent_at, is_mine=True, show_time=False, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { border: none; background: transparent; }")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 1, 8, 1)
        lay.setSpacing(2)

        # Bubble row
        bubble_row = QHBoxLayout()
        bubble_row.setContentsMargins(0, 0, 0, 0)

        MAX_W = 300

        from PyQt5.QtGui import QFontMetrics, QFont
        fm = QFontMetrics(QFont("Segoe UI", 10))
        # Do chieu rong 1 dong
        single_w = fm.horizontalAdvance(content) + 28
        actual_w = min(single_w, MAX_W)

        bubble = QLabel(content)
        bubble.setWordWrap(True)
        bubble.setFixedWidth(actual_w)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if is_mine:
            bubble.setStyleSheet(
                f"background: {styles.PRIMARY}; color: white;"
                f"border-radius: 16px; border-bottom-right-radius: 4px;"
                f"padding: 8px 12px; font-size: 13px; border: none;")
            bubble_row.addStretch()
            bubble_row.addWidget(bubble)
        else:
            bubble.setStyleSheet(
                f"background: {styles.WHITE}; color: {styles.TEXT_DARK};"
                f"border-radius: 16px; border-bottom-left-radius: 4px;"
                f"border: 1px solid {styles.BORDER};"
                f"padding: 8px 12px; font-size: 13px;")
            bubble_row.addWidget(bubble)
            bubble_row.addStretch()

        lay.addLayout(bubble_row)

        # Thoi gian - chi hien khi show_time=True
        if show_time:
            try:
                dt = datetime.strptime(sent_at, "%Y-%m-%d %H:%M:%S")
                time_str = dt.strftime("%H:%M")
            except:
                time_str = sent_at or ""
            time_lbl = QLabel(time_str)
            time_lbl.setStyleSheet(
                f"color: {styles.TEXT_MUTED}; font-size: 11px; border: none; background: transparent;")
            time_lbl.setAlignment(Qt.AlignRight if is_mine else Qt.AlignLeft)
            lay.addWidget(time_lbl)


class StudentItem(QWidget):
    """Widget hien thi 1 sinh vien trong danh sach ben trai."""
    def __init__(self, student_id, name, faculty, last_msg, unread, is_overdue=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        # Avatar
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "SV"
        av_bg = "#FCEBEB" if is_overdue else styles.PRIMARY_LIGHT
        av_fg = "#A32D2D" if is_overdue else styles.PRIMARY
        av = QLabel(initials)
        av.setFixedSize(40, 40)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(
            f"background: {av_bg}; color: {av_fg};"
            f"border-radius: 20px; font-weight: bold; font-size: 13px; border: none;")
        lay.addWidget(av)

        # Info
        info = QVBoxLayout(); info.setSpacing(2)
        name_row = QHBoxLayout(); name_row.setSpacing(6)
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            f"color: {styles.TEXT_DARK}; font-weight: 600; font-size: 13px; border: none;")
        name_row.addWidget(name_lbl)
        if is_overdue:
            od_badge = QLabel("Quá hạn")
            od_badge.setStyleSheet(
                "background: #FCEBEB; color: #A32D2D; border-radius: 8px;"
                "padding: 1px 6px; font-size: 10px; font-weight: 600; border: none;")
            name_row.addWidget(od_badge)
        name_row.addStretch()
        sub = QLabel(last_msg[:40] + "..." if last_msg and len(last_msg) > 40 else (last_msg or faculty or ""))
        sub.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 12px; border: none;")
        info.addLayout(name_row)
        info.addWidget(sub)
        lay.addLayout(info)
        lay.addStretch()

        # Unread badge
        if unread and unread > 0:
            badge = QLabel(str(unread))
            badge.setFixedSize(22, 22)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(
                f"background: {styles.DANGER}; color: white;"
                f"border-radius: 11px; font-size: 11px; font-weight: bold; border: none;")
            lay.addWidget(badge)


class MessageWindow(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.selected_student = None
        self._build()
        self._load_students()

        # Auto refresh moi 10 giay
        self.timer = QTimer()
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start(10000)

    def _build(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # LEFT: danh sach sinh vien
        left = QFrame()
        left.setFixedWidth(300)
        left.setStyleSheet(
            f"QFrame {{ background: {styles.WHITE}; border-right: 1px solid {styles.BORDER}; }}")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        # Header trai
        hdr_l = QWidget()
        hdr_l.setFixedHeight(56)
        hdr_l.setStyleSheet(
            f"background: {styles.WHITE}; border-bottom: 1px solid {styles.BORDER};")
        hl = QHBoxLayout(hdr_l)
        hl.setContentsMargins(16, 0, 16, 0)
        title = QLabel("Tin nhắn")
        title.setStyleSheet(
            f"color: {styles.TEXT_DARK}; font-weight: bold; font-size: 15px; border: none;")
        btn_ref = QPushButton("↻")
        btn_ref.setStyleSheet(styles.BTN_OUTLINE)
        btn_ref.setFixedSize(32, 32)
        btn_ref.clicked.connect(self._load_students)
        hl.addWidget(title); hl.addStretch(); hl.addWidget(btn_ref)
        ll.addWidget(hdr_l)

        # Search
        search_w = QWidget()
        search_w.setStyleSheet(f"background: {styles.BG}; border: none;")
        sl = QHBoxLayout(search_w)
        sl.setContentsMargins(12, 8, 12, 8)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm sinh viên...")
        self.inp_search.setStyleSheet(styles.INPUT)
        self.inp_search.setFixedHeight(36)
        self.inp_search.textChanged.connect(self._filter_students)
        sl.addWidget(self.inp_search)
        ll.addWidget(search_w)

        # Filter bar
        filter_w = QWidget()
        filter_w.setStyleSheet(f"background: {styles.WHITE}; border-bottom: 1px solid {styles.BORDER};")
        fl2 = QHBoxLayout(filter_w)
        fl2.setContentsMargins(12, 6, 12, 6); fl2.setSpacing(6)
        self.cmb_filter = QComboBox()
        self.cmb_filter.setStyleSheet(styles.COMBO)
        self.cmb_filter.setFixedHeight(32)
        self.cmb_filter.addItems(["Tất cả", "Chưa đọc", "Quá hạn"])
        self.cmb_filter.currentTextChanged.connect(self._filter_students)
        fl2.addWidget(QLabel("Lọc:"))
        fl2.addWidget(self.cmb_filter)
        fl2.addStretch()
        ll.addWidget(filter_w)

        # Scroll area cho danh sach SV
        self.sv_scroll = QScrollArea()
        self.sv_scroll.setWidgetResizable(True)
        self.sv_scroll.setFrameShape(QFrame.NoFrame)
        self.sv_scroll.setStyleSheet("background: transparent; border: none;")
        self.sv_container = QWidget()
        self.sv_container.setStyleSheet("background: transparent;")
        self.sv_layout = QVBoxLayout(self.sv_container)
        self.sv_layout.setContentsMargins(0, 0, 0, 0)
        self.sv_layout.setSpacing(0)
        self.sv_layout.addStretch()
        self.sv_scroll.setWidget(self.sv_container)
        ll.addWidget(self.sv_scroll)
        main.addWidget(left)

        # RIGHT: khung chat
        right = QWidget()
        right.setStyleSheet(f"background: {styles.BG};")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # Header phai
        self.chat_header = QWidget()
        self.chat_header.setFixedHeight(56)
        self.chat_header.setStyleSheet(
            f"background: {styles.WHITE}; border-bottom: 1px solid {styles.BORDER};")
        chl = QHBoxLayout(self.chat_header)
        chl.setContentsMargins(20, 0, 20, 0)
        self.lbl_chat_name = QLabel("Chọn sinh viên để bắt đầu")
        self.lbl_chat_name.setStyleSheet(
            f"color: {styles.TEXT_DARK}; font-weight: bold; font-size: 14px; border: none;")
        self.lbl_chat_sub = QLabel("")
        self.lbl_chat_sub.setStyleSheet(
            f"color: {styles.TEXT_MUTED}; font-size: 12px; border: none;")
        name_col = QVBoxLayout(); name_col.setSpacing(1)
        name_col.addWidget(self.lbl_chat_name)
        name_col.addWidget(self.lbl_chat_sub)
        chl.addLayout(name_col); chl.addStretch()
        rl.addWidget(self.chat_header)

        # Vung hien thi tin nhan
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
        input_bar.setStyleSheet(
            f"background: {styles.WHITE}; border-top: 1px solid {styles.BORDER};")
        il = QHBoxLayout(input_bar)
        il.setContentsMargins(16, 12, 16, 12)
        il.setSpacing(10)
        self.inp_msg = QLineEdit()
        self.inp_msg.setPlaceholderText("Nhập tin nhắn...")
        self.inp_msg.setStyleSheet(styles.INPUT)
        self.inp_msg.setFixedHeight(44)
        self.inp_msg.returnPressed.connect(self._send)
        btn_send = QPushButton("Gửi ➤")
        btn_send.setStyleSheet(styles.BTN_PRIMARY)
        btn_send.setFixedHeight(44)
        btn_send.setMinimumWidth(90)
        btn_send.clicked.connect(self._send)
        il.addWidget(self.inp_msg); il.addWidget(btn_send)
        rl.addWidget(input_bar)
        main.addWidget(right)

        self.all_students = []

    def _load_students(self):
        from core.services.message_service import get_student_list_with_messages
        from database.db import get_connection
        from datetime import datetime
        self.all_students = get_student_list_with_messages()
        today = datetime.now().strftime("%Y-%m-%d")
        # Danh dau sinh vien qua han
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT StudentID FROM Borrow
                WHERE Status='Overdue'
            """)
            overdue_ids = set(r[0] for r in cur.fetchall())
            conn.close()
        except: overdue_ids = set()
        for s in self.all_students:
            s["_is_overdue"] = s.get("StudentID","") in overdue_ids
        self._filter_students()

    def _filter_students(self):
        kw     = self.inp_search.text().strip().lower()
        mode   = self.cmb_filter.currentText() if hasattr(self, "cmb_filter") else "Tất cả"
        result = list(self.all_students)

        # Loc theo tu khoa
        if kw:
            result = [s for s in result
                      if kw in s.get("Name","").lower()
                      or kw in s.get("StudentID","").lower()]

        # Loc theo mode
        if mode == "Chưa đọc":
            result = [s for s in result if (s.get("UnreadCount") or 0) > 0]
        elif mode == "Quá hạn":
            result = [s for s in result if s.get("_is_overdue")]

        # Sap xep: co tin nhan len dau, trong do unread > overdue > co tin > khong tin
        def sort_key(s):
            has_msg  = 1 if s.get("LastMessage") else 0
            unread   = s.get("UnreadCount") or 0
            overdue  = 1 if s.get("_is_overdue") else 0
            last_at  = s.get("LastAt") or ""
            return (-has_msg, -unread, -overdue, -ord(last_at[0]) if last_at else 0)

        result.sort(key=sort_key)
        self._render_students(result)

    def _render_students(self, students):
        # Xoa danh sach cu
        while self.sv_layout.count() > 1:
            item = self.sv_layout.takeAt(0)
            if item is None: break
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        for s in students:
            sid      = s.get("StudentID","")
            name     = s.get("Name","")
            faculty  = s.get("Faculty","") or ""
            last_msg = s.get("LastMessage","") or ""
            unread   = s.get("UnreadCount", 0) or 0

            is_overdue = s.get("_is_overdue", False)
            item_w = StudentItem(sid, name, faculty, last_msg, unread, is_overdue)
            item_w.setCursor(Qt.PointingHandCursor)

            # Highlight neu dang chon
            if self.selected_student and self.selected_student.get("StudentID") == sid:
                item_w.setStyleSheet(
                    f"background: {styles.PRIMARY_LIGHT}; border-left: 3px solid {styles.PRIMARY};")
            else:
                item_w.setStyleSheet(
                    "background: transparent;"
                    "border-bottom: 1px solid #F1F5F9;")
                item_w.installEventFilter(self)

            item_w.mousePressEvent = lambda e, st=s: self._select_student(st)

            div = QFrame(); div.setFrameShape(QFrame.HLine)
            div.setStyleSheet(f"background: {styles.BORDER}; max-height: 1px; border: none;")

            self.sv_layout.insertWidget(self.sv_layout.count()-1, item_w)
            self.sv_layout.insertWidget(self.sv_layout.count()-1, div)

    def _select_student(self, student):
        self.selected_student = student
        sid  = student.get("StudentID","")
        name = student.get("Name","")
        fac  = student.get("Faculty","") or ""

        self.lbl_chat_name.setText(name)
        self.lbl_chat_sub.setText(f"{sid} — {fac}")

        # Mark as read
        from core.services.message_service import mark_as_read
        staff_id = self.current_user.get("StaffID","")
        mark_as_read(staff_id, sid)

        self._load_messages()
        self._render_students(self.all_students)

    def _load_messages(self):
        if not self.selected_student: return
        from core.services.message_service import get_conversation
        staff_id  = self.current_user.get("StaffID","")
        student_id = self.selected_student.get("StudentID","")
        staff_name = self.current_user.get("Name","Admin")

        msgs = get_conversation(staff_id, student_id)

        # Xoa tin nhan cu
        while self.msg_layout.count() > 1:
            item = self.msg_layout.takeAt(0)
            if item is None: break
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        if not msgs:
            no_msg = QLabel("Chưa có tin nhắn nào.\nHãy bắt đầu cuộc trò chuyện!")
            no_msg.setAlignment(Qt.AlignCenter)
            no_msg.setStyleSheet(
                f"color: {styles.TEXT_MUTED}; font-size: 13px; border: none;")
            self.msg_layout.insertWidget(0, no_msg)
        else:
            idx = 0
            prev_dt = None
            prev_is_mine = None
            for i, msg in enumerate(msgs):
                is_mine  = msg.get("SenderType") == "staff"
                sent_at  = msg.get("SentAt","")

                # Tinh thoi gian
                try:
                    cur_dt = datetime.strptime(sent_at, "%Y-%m-%d %H:%M:%S")
                except:
                    cur_dt = None

                # Them time divider neu cach nhau > 15 phut
                if cur_dt and prev_dt:
                    diff = (cur_dt - prev_dt).total_seconds() / 60
                    if diff >= 15:
                        time_str = cur_dt.strftime("%H:%M - %d/%m")
                        divider = TimeDivider(time_str)
                        self.msg_layout.insertWidget(idx, divider)
                        idx += 1
                elif cur_dt and not prev_dt:
                    # Tin dau tien - hien gio
                    time_str = cur_dt.strftime("%H:%M - %d/%m")
                    divider = TimeDivider(time_str)
                    self.msg_layout.insertWidget(idx, divider)
                    idx += 1

                # show_time chi hien khi tin cuoi trong nhom hoac truoc divider tiep theo
                is_last = (i == len(msgs) - 1)
                next_msg = msgs[i+1] if not is_last else None
                show_time = False
                if is_last:
                    show_time = True
                elif next_msg:
                    try:
                        next_dt = datetime.strptime(next_msg.get("SentAt",""), "%Y-%m-%d %H:%M:%S")
                        if cur_dt and (next_dt - cur_dt).total_seconds() / 60 >= 15:
                            show_time = True
                        elif next_msg.get("SenderType") != msg.get("SenderType"):
                            show_time = False
                    except:
                        pass

                bubble = BubbleWidget(
                    msg.get("Content",""),
                    sent_at,
                    is_mine=is_mine,
                    show_time=show_time
                )
                self.msg_layout.insertWidget(idx, bubble)
                idx += 1
                prev_dt = cur_dt
                prev_is_mine = is_mine

        # Scroll xuong cuoi
        QTimer.singleShot(100, lambda: self.msg_scroll.verticalScrollBar().setValue(
            self.msg_scroll.verticalScrollBar().maximum()))

    def _send(self):
        if not self.selected_student:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn sinh viên để nhắn tin.")
            return
        content = self.inp_msg.text().strip()
        if not content: return

        from core.services.message_service import send_message
        staff_id   = self.current_user.get("StaffID","")
        student_id = self.selected_student.get("StudentID","")

        send_message(staff_id, "staff", student_id, "student", content)
        self.inp_msg.clear()
        self._load_messages()
        self._load_students()

    def _auto_refresh(self):
        if self.selected_student:
            self._load_messages()
        self._load_students()

    def refresh(self):
        self._load_students()