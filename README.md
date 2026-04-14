Tổng quan chức năng ứng dụng Library Management System
QUẢN TRỊ VIÊN
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

CHỨC NĂNG CỦA ĐỘC GIẢ 

1. Khám phá và Tìm kiếm sách (Tìm kiếm cơ bản & Nâng cao):
Tìm kiếm nhanh: Tìm kiếm sách trực tiếp trên Trang chủ bằng cách nhập Tên sách, Tác giả hoặc mã ISBN.
Bộ lọc nâng cao: Độc giả có thể dễ dàng lọc danh sách sách thư viện theo Chuyên ngành (Lập trình, CNTT, Ngoại ngữ, Kinh tế...), Tác giả, và Trạng thái (Sách còn sẵn hay đang bị người khác mượn).
Xem nhanh các đầu Sách mới nhập từ hệ thống.

2. Đăng ký mượn sách trực tuyến:
Khi nhấn vào một cuốn sách, độc giả có thể xem chi tiết (Nhà xuất bản, Năm phát hành, Vị trí trên kệ, tình trạng số lượng).
Nếu sách hiển thị "CÒN SẴN", độc giả có thể bấm nút "📖 Đăng ký mượn sách" để xác nhận mượn trực tiếp trên hệ thống mà không cần thẻ giấy.

3. Quản lý Thư viện Cá nhân (Dashboard): Độc giả có một bảng điều khiển cá nhân (Dashboard) hiển thị mã sinh viên và các thông tin chi tiết:
Thống kê cá nhân: Tổng số sách Đang mượn, Đã trả, Quá hạn trả, và Tổng lượt mượn.
Đang mượn: Có một thanh tiến độ (Progress bar) thông minh cảnh báo ngày còn lại phải trả sách (Màu xanh: an toàn, Màu vàng/Đỏ: sắp tới hạn/quá hạn).
Lịch sử mượn: Xem lại toàn bộ lịch sử các giao dịch mượn/trả sách trước đây của bản thân.
Phí phạt: Xem các khoản phí phạt nếu trả sách quá hạn, làm mất hoặc hỏng sách.

Tree derectory project

<img width="156" height="447" alt="image" src="https://github.com/user-attachments/assets/47dee2a6-5c14-4fdd-b128-29c44fd28dfc" />

<img width="163" height="177" alt="image" src="https://github.com/user-attachments/assets/730c8a13-4b16-4e5a-bcd7-5b5600d3bf12" />

Giao diện 
<img width="201" height="258" alt="image" src="https://github.com/user-attachments/assets/44fefd08-c08a-41f0-998f-d490b6c7a276" />

<img width="400" height="228" alt="image" src="https://github.com/user-attachments/assets/b5ec1614-6910-46e3-95a9-9ec0a84870f9" />

<img width="436" height="121" alt="image" src="https://github.com/user-attachments/assets/4a8aba48-afdd-4fd0-8c96-f862e06d51b0" />

<img width="446" height="119" alt="image" src="https://github.com/user-attachments/assets/8a8a6ab6-ad65-4989-9712-75834ab28ef9" />

<img width="495" height="125" alt="image" src="https://github.com/user-attachments/assets/f080a2a1-273b-42d6-9031-35c2898544d7" />

<img width="482" height="124" alt="image" src="https://github.com/user-attachments/assets/acb0957e-6b33-472c-9992-2984f7845122" />

<img width="400" height="124" alt="image" src="https://github.com/user-attachments/assets/9467b364-0bbf-4794-b9a4-1d57cde321b5" />

<img width="420" height="180" alt="image" src="https://github.com/user-attachments/assets/a79e3760-7f3f-424b-8f74-c79fc3984171" />

<img width="420" height="180" alt="image" src="https://github.com/user-attachments/assets/89fd36b3-fecb-45c9-b944-a3a13bf7c3b6" />

<img width="420" height="180" alt="image" src="https://github.com/user-attachments/assets/38c58e18-eb6f-4ca1-a62d-d01b142bc1ce" />

<img width="420" height="180" alt="image" src="https://github.com/user-attachments/assets/bf52e261-b3a8-4704-bfd8-f4e8d638231a" />

<img width="420" height="180" alt="image" src="https://github.com/user-attachments/assets/4c1be5a3-19a3-41de-993c-00ffd0d8b80b" />

<img width="420" height="180" alt="image" src="https://github.com/user-attachments/assets/0c951ef3-a809-4237-8405-a7762cec94ba" />


