# Cau hinh toan cuc
import os

# Duong dan
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "library.db")

# Quy tac muon sach
DEFAULT_BORROW_DAYS = 14
MAX_BORROW_LIMIT = 3
FINE_PER_DAY = 2000  # dong

# Giao dien
COLOR_PRIMARY = "#8AAAE5"
COLOR_PRIMARY_DARK = "#6B8FD4"
COLOR_PRIMARY_LIGHT = "#C5D6F5"
COLOR_PRIMARY_BG = "#EEF3FC"
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT_DARK = "#1A2540"
COLOR_TEXT_MID = "#4A5568"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_BORDER = "#DDE6F8"
COLOR_SUCCESS = "#48BB78"
COLOR_WARNING = "#F6AD55"
COLOR_DANGER = "#FC8181"

# App info
APP_NAME = "Library Management System"
APP_VERSION = "1.0.0"