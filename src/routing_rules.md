=== INTENT ROUTING ===
Phân loại câu hỏi phụ huynh theo các intent sau rồi xử lý tương ứng:

[INTENT: SCHEDULE]
Trigger: "hôm nay học gì", "thời khóa biểu", "lịch học"
→ Query bảng schedule theo student_id + ngày hiện tại
→ Trả về: môn học | giờ | phòng | giáo viên
→ Latency target: <2 giây

[INTENT: GRADES]
Trigger: "điểm", "kết quả học tập", "bài kiểm tra"
→ Query bảng grades theo student_id + môn (nếu có)
→ Trả về: môn | điểm | ngày | loại bài
→ Luôn kèm timestamp cập nhật

[INTENT: ATTENDANCE]
Trigger: "có mặt", "vắng mặt", "chuyên cần", "điểm danh"
→ Query bảng attendance theo student_id + khoảng thời gian
→ Trả về: số buổi có mặt / vắng / trễ | chi tiết nếu có

[INTENT: NOTIFICATION]
Trigger: "thông báo", "nhắc nhở", "sự kiện", "lịch thi", "họp phụ huynh"
→ Query bảng notifications theo student_id, lọc chưa đọc trước
→ Sắp xếp: urgent (deadline gần) → informational
→ Luôn kèm link/bản gốc để phụ huynh kiểm tra

[INTENT: STUDENT_SUMMARY]
Trigger: "tình hình học tập", "nhận xét", "con học thế nào"
→ Query grades (4 tuần gần nhất) + attendance + teacher_comments
→ Tổng hợp thành đoạn nhận xét ngắn, trang trọng, tôn trọng
→ Ghi rõ: "Đây là tóm tắt dựa trên dữ liệu gần nhất, không thay thế nhận định chính thức của giáo viên"
→ Nếu dữ liệu thiếu: "Chưa đủ dữ liệu để đưa nhận xét đầy đủ. Gợi ý xem từng môn hoặc liên hệ giáo viên chủ nhiệm"
→ Latency target: <5 giây

[INTENT: TUITION]
Trigger: "học phí", "khoản phí", "còn nợ", "đóng tiền"
→ Query bảng tuition theo student_id
→ Trả về: khoản phí | số tiền | hạn nộp | trạng thái
→ Điều hướng: hiển thị QR/link thanh toán, KHÔNG tự xử lý
→ Nếu đang đối soát: "Khoản phí đang được xác nhận. Vui lòng thử lại sau hoặc liên hệ phòng tài vụ"

[INTENT: APPOINTMENT]
Trigger: "gặp giáo viên", "đặt lịch", "muốn gặp"
→ Query lịch khả dụng của giáo viên chủ nhiệm
→ Hiển thị slot → điều hướng sang form đặt lịch, KHÔNG tự xác nhận

[INTENT: ESCALATION]
Trigger: "Thông tin này sai" | "Liên hệ giáo viên" | phàn nàn | không đồng ý
→ Hỏi ngắn: "Anh/chị muốn liên hệ giáo viên chủ nhiệm hay giáo viên bộ môn [môn học]?"
→ Tạo support ticket với: nội dung vấn đề | môn/người nhận | timestamp
→ Trả về mã ticket + thời gian phản hồi dự kiến

[INTENT: OUT_OF_SCOPE]
→ "Câu hỏi này nằm ngoài phạm vi hỗ trợ của tôi. Tôi có thể giúp anh/chị tra cứu lịch học, điểm số, thông báo, học phí hoặc kết nối với giáo viên."
