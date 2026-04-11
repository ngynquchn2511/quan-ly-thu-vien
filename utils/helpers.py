# Ham tien ich chung
from datetime import datetime


def format_date(date_str: str, in_fmt="%Y-%m-%d", out_fmt="%d/%m/%Y") -> str:
    try:
        return datetime.strptime(date_str, in_fmt).strftime(out_fmt)
    except Exception:
        return date_str or ""


def today_str(fmt="%Y-%m-%d") -> str:
    return datetime.now().strftime(fmt)


def format_currency(amount: float) -> str:
    return f"{amount:,.0f}d"


def get_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"