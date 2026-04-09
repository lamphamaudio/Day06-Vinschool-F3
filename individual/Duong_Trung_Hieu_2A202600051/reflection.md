# Individual reflection — Dương Trung Hiếu (2A202600051)

## 1. Role
- Phụ trách phát triển tool tra cứu học phí, điều hướng giao dịch và hệ thống ghi nhận khiếu nại (Escalation/Support Tickets).
- Viết phần Feasibility (Tính khả thi và Rủi ro) trong tài liệu SPEC.

## 2. Đóng góp cụ thể
- Xây dựng các tool `get_tuition_status`, `initiate_fee_payment` và `report_issue_to_teacher` trong `tools.py`.
- Viết các hàm tương tác với CSDL trong `database.py` để truy vấn bảng `fee_records` và ghi dữ liệu vào bảng `support_tickets`.
- Định nghĩa chi phí cost/latency và các rủi ro kỹ thuật (Feasibility) của hệ thống trong tài liệu SPEC.

## 3. SPEC mạnh/yếu
- **Mạnh nhất:** Phần Feasibility đã chỉ ra được risk lớn nhất là hệ thống tự động chốt giao dịch khi chưa có xác nhận. Điều này dẫn đến quyết định thiết kế AI theo hướng Augmentation (chỉ hiển thị link/QR để phụ huynh tự thanh toán).
- **Yếu nhất:** Phần ước tính cost inference (~$15-25/ngày cho Realistic) mang tính ước lượng khá thô. Chưa tính toán kỹ chi phí duy trì database PostgreSQL và chi phí lưu trữ log hội thoại (`ai_audit_logs`) khi scale lên hàng nghìn user.

## 4. Đóng góp khác
- Thiết kế luồng Fallback cho tool thanh toán: Khi khoản phí bị quá hạn (overdue), ép prompt AI không được hứa hẹn gì thêm mà phải điều hướng chính xác vào link payment hoặc sinh mã QR.
- Hỗ trợ xây dựng mock data cho các khoản phí (tuition, meal) và các ticket khiếu nại mẫu trong file `mock_data.sql`.

## 5. Điều học được
Làm việc với các tool mang tính giao dịch (tiền bạc, khiếu nại), tôi nhận ra AI rất hay bị "ảo giác" (hallucinate). Ban đầu, nếu hàm `initiate_fee_payment` trả về link, AI thường tự động thêm câu "Anh/chị đã thanh toán thành công". Tôi đã học được cách phải tinh chỉnh system prompt cực kỳ gắt gao: "chỉ hướng dẫn và xác nhận bước tiếp theo; không được giả định giao dịch cuối cùng đã hoàn tất" để kìm hãm sự "nhiệt tình thái quá" của LLM.

## 6. Nếu làm lại
Tôi sẽ làm thêm tính năng tích hợp gửi email thông báo thực tế (bằng SMTP) khi tool `report_issue_to_teacher` được gọi, thay vì chỉ ghi log xuống bảng `support_tickets`. Như vậy bản demo sẽ mang tính end-to-end và thuyết phục hơn.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI hỗ trợ viết các câu lệnh SQL INSERT phức tạp với khóa ngoại (foreign keys) để mock hàng loạt dữ liệu học phí và ticket hợp lệ, tiết kiệm rất nhiều thời gian test.
- **Sai/mislead:** Khi nhờ AI viết tool đặt lịch (`book_teacher_meeting`), AI tự động sinh ra luồng xử lý thời gian (datetime) rất cồng kềnh và thỉnh thoảng so sánh sai múi giờ, khiến tool báo "giáo viên hết lịch" dù dữ liệu vẫn còn. Tôi phải tự viết lại hàm `get_available_meeting_slots` bằng logic Python cơ bản thay vì phụ thuộc AI.