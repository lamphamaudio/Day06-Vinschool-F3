# Individual reflection — Nguyễn Đức Hải (2A202600149)

## 1. Role

 Phụ trách phát triển tool tra cứu kết quả học tập, đánh giá của giáo viên và đưa ra đánh ra chung; thiết kế conversation flow tương ứng & viết phần Eval metric trong SPEC.

## 2. Đóng góp cụ thể

- Xây dựng và tích hợp tool lấy kết quả học tập và nhận xét/đánh giá của học sinh.
- Thiết kế conversation flow cho chức năng hỏi đáp về học tập (nhận diện ý định -> gọi tool tra cứu -> xử lý dữ liệu -> AI sinh phản hồi).
- Viết và định nghĩa hệ thống phân tích, đánh giá hiệu năng (Eval metrics) trong tài liệu SPEC.

## 3. SPEC mạnh/yếu

- **Mạnh nhất:** Phần Eval metrics được định nghĩa rõ ràng, cụ thể hoá được cách đo lường độ chính xác và chất lượng phản hồi của agent thay vì chỉ đánh giá cảm tính.
- **Yếu nhất:** Assumption về chất lượng dữ liệu điểm số. Các kịch bản giả định database hoàn hảo, nhưng thực tế có thể gặp các case như thiếu điểm thành phần, chưa cập nhật nhận xét, nhưng trong SPEC chưa bao phủ hết hướng xử lý dự phòng (fallback) cho các trường hợp này.

## 4. Đóng góp khác

- Tham gia test và tinh chỉnh prompt cho tool nhận xét học tập để đảm bảo văn phong chuyên nghiệp, phù hợp với từng đối tượng (phụ huynh/học sinh).
- Hỗ trợ ráp nối luồng xử lý lỗi khi tool thất bại hoặc API timeout vào kiến trúc LangGraph chung.

## 5. Điều học được

Trước đây chỉ nghĩ đơn thuần ráp tool gọi API vào chatbot là xong. Nhờ tự mình viết Eval metric và làm flow phần học tập mới hiểu rằng việc xử lý dữ liệu đầu ra từ tool sao cho khéo (ví dụ: điểm kém thì AI cần feedback ra sao cho tinh tế) và đo lường được chất lượng (độ bao phủ thông tin, hallucination rate) quan trọng bằng việc code ra chức năng. Thiết kế metric đúng thì mới hướng AI trả lời đúng yêu cầu sản phẩm.

## 6. Nếu làm lại

Sẽ dành nhiều thời gian hơn để làm rõ các edge cases trong flow học tập từ sớm (khi gọi database lỗi, học sinh chưa có điểm, hay hỏi điểm những môn không tồn tại) và mock dữ liệu test đa dạng hơn thay vì chỉ focus vào happy path. 

## 7. AI giúp gì / AI sai gì

- **Giúp:** Dùng LLM để brainstorm các tiêu chí đánh giá cho Eval metrics cực kỳ hiệu quả, giúp liệt kê ra chi tiết các yếu tố như *Groundedness* hay *Tone của câu trả lời*. Tạo nhanh mock data để test tool lấy kết quả học tập.
- **Sai/mislead:** Khi nhờ AI viết mẫu luồng conversation flow, AI thường có xu hướng vẽ thêm quá nhiều bước thừa (như đòi xác thực OTP dù đã login, hỏi thêm quá nhiều câu không cần thiết) làm luồng trở nên cồng kềnh, khiến mình phải cắt gọt lại để bám sát thực tế Hackathon.

