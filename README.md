Tổng quan chức năng ứng dụng Library Management System

1. Đăng nhập

Nhập tài khoản + mật khẩu, hệ thống tự nhận quyền từ DB
Sai mật khẩu → hiệu ứng lắc card + thông báo lỗi
Đúng → chuyển thẳng vào Dashboard theo role


2. Dashboard

Hiển thị 4 thống kê realtime: tổng sách / sinh viên / đang mượn / quá hạn
Danh sách sách quá hạn kèm tên SV + số ngày + tiền phạt
Top 3 sách được mượn nhiều nhất
Hoạt động gần đây
Badge đỏ trên topbar cảnh báo số sách quá hạn
Tự động cập nhật trạng thái Overdue khi mở app


3. Quản lý Sách

Xem danh sách toàn bộ sách trong thư viện
Tìm kiếm realtime theo tên / tác giả / ISBN
Lọc theo thể loại
Thêm sách mới — form đầy đủ: mã, tên, tác giả, thể loại, NXB, năm, ISBN, số lượng, vị trí kệ
Sửa thông tin sách — điền sẵn dữ liệu cũ
Xóa sách — có confirm dialog
Badge trạng thái: Còn sách / Gần hết / Hết sách dựa theo số lượng còn lại


4. Quản lý Độc giả

Xem danh sách sinh viên đăng ký thư viện
Tìm kiếm theo tên / mã SV / số điện thoại
Lọc theo khoa
Thêm độc giả mới — mã SV, họ tên, khoa, lớp, SĐT, email, hạn thẻ
Sửa thông tin — gia hạn thẻ thư viện
Xóa độc giả — có confirm dialog
Badge trạng thái thẻ: Hợp lệ / Hết hạn


5. Mượn / Trả sách
Mượn:

Nhập mã SV → hiển thị thông tin SV + kiểm tra thẻ còn hạn không
Nhập mã sách → hiển thị thông tin sách + số lượng còn lại
Tự động tính hạn trả (14 ngày)
Kiểm tra ràng buộc trước khi cho mượn:

Thẻ SV còn hạn
SV chưa mượn quá 3 cuốn
SV không có sách quá hạn chưa trả
Sách còn trong kho

Trả:

Chọn phiếu mượn → xác nhận trả
Tự động tính tiền phạt nếu quá hạn (2.000đ/ngày)
Cập nhật số lượng sách còn lại

Danh sách đang mượn:

Xem toàn bộ phiếu đang mượn
Badge trạng thái: OK / Sắp hạn / Quá hạn


6. Báo cáo & Thống kê

Xuất báo cáo mượn trả ra file Excel
Xuất danh sách sách quá hạn kèm tiền phạt
Thống kê sách mượn nhiều nhất
Thống kê độc giả hoạt động
Biểu đồ mượn sách theo thể loại
Báo cáo tiền phạt thu được


7. Quản lý Nhân viên (chỉ Admin thấy)

Xem danh sách nhân viên
Thêm tài khoản nhân viên mới
Phân quyền: Admin / Staff
Xóa nhân viên
Mật khẩu được mã hóa SHA-256
<img width="501" height="558" alt="image" src="https://github.com/user-attachments/assets/44fefd08-c08a-41f0-998f-d490b6c7a276" />

