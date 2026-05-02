# Xuat bao cao bao muon tra khong can pandas/openpyxl
import csv
from database.db import get_connection


def export_borrow_report(path):
    """Xuat bao cao muon tra ra file CSV (ke ca khi duoi file la .csv)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            b.BorrowID,
            s.StudentID,
            s.Name,
            bk.BookID,
            bk.Title,
            b.BorrowDate,
            b.DueDate,
            COALESCE(b.ReturnDate, ''),
            b.Status,
            COALESCE(b.FineAmount, 0),
            CASE COALESCE(b.FinePaid, 0) WHEN 1 THEN 'Đã nộp' ELSE 'Chưa nộp' END
        FROM Borrow b
        JOIN Students s ON b.StudentID = s.StudentID
        JOIN Books bk ON b.BookID = bk.BookID
        ORDER BY b.BorrowDate DESC, b.BorrowID DESC
    """)
    rows = cur.fetchall()
    conn.close()

    headers = [
        "Mã phiếu",
        "Mã sinh viên",
        "Họ tên",
        "Mã sách",
        "Tên sách",
        "Ngày mượn",
        "Hạn trả",
        "Ngày trả",
        "Trạng thái",
        "Tiền phạt",
        "Thanh toán phạt",
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(list(r))

    return path
