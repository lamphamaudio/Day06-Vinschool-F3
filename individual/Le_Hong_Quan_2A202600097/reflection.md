# Individual reflection — Lê Hồng Quân (2A202600097)

## 1. Role

Phụ trách xây dựng SPEC tổng thể cho dự án, đảm nhận vai trò lead team để định hướng tiến độ và phân chia công việc, đồng thời review source code để đảm bảo các phần ghép nối với nhau hợp lý.

## 2. Đóng góp cụ thể

- Chia task cho các thành viên theo từng mảng như SPEC, database, tool, UI và phần thuyết trình để nhóm làm việc song song hiệu quả hơn.
- Thiết kế database cho bài toán phụ huynh - nhà trường, xác định các bảng dữ liệu chính và quan hệ giữa phụ huynh, học sinh, giáo viên, điểm số, thông báo, học phí và hội thoại.
- Phát triển các tool `get_teacher_contact_info` và `get_teacher_comments` để hỗ trợ AI tra cứu thông tin liên hệ giáo viên và nhận xét của giáo viên dành cho học sinh.
- Review source code trong quá trình làm để phát hiện các phần chưa hợp lý trong flow, cấu trúc dữ liệu và cách tích hợp agent với database.
- Làm slide để tổng hợp bài toán, kiến trúc giải pháp, điểm nổi bật của sản phẩm và chuẩn bị cho phần trình bày cuối.

## 3. SPEC mạnh/yếu

- **Mạnh nhất:** SPEC xác định khá rõ bài toán thực tế, user chính, phạm vi MVP và các tiêu chí đánh giá chất lượng như grounded precision, escalation routing hay latency. Điều này giúp cả nhóm không chỉ code theo cảm tính mà luôn có một khung chung để bám vào.
- **Yếu nhất:** Một số phần trong SPEC vẫn thiên về mức định hướng hơn là operational detail. Chẳng hạn, phần edge case cho dữ liệu chưa đồng bộ, dữ liệu sai hoặc flow escalation nhiều bước vẫn chưa được đặc tả sâu bằng những scenario thật cụ thể, nên khi code nhóm vẫn phải tự quyết định thêm trong lúc triển khai.

## 4. Đóng góp khác

- Hỗ trợ các bạn trong nhóm khi gặp khó khăn về task, đặc biệt ở giai đoạn ghép các phần riêng lẻ thành một flow thống nhất.
- Là người thuyết trình chính, chịu trách nhiệm trình bày bài toán, cách nhóm tiếp cận và những điểm nổi bật về AI product trước lớp/ban giám khảo.

## 5. Điều học được

Điều mình học được rõ nhất là việc brainstorm cho dự án cực kỳ quan trọng. Trước đây mình thường nhìn bài toán theo các happy case là chính, nhưng qua hackathon này mới thấy nếu không nghĩ sớm về failure modes, dữ liệu thiếu, user phản hồi sai hoặc flow bị ngắt giữa chừng thì sản phẩm AI rất dễ trông ổn ở bản demo nhưng lại yếu khi dùng thực tế.

## 6. Nếu làm lại

Nếu được làm lại, mình sẽ dành thêm thời gian ngay từ đầu để chuẩn hóa spec thành các scenario cụ thể hơn cho từng use case, đặc biệt là các tình huống sai dữ liệu, escalation và quyền truy cập. Mình cũng sẽ tổ chức review chéo sớm hơn giữa các thành viên để phát hiện xung đột giữa prompt, tool và database trước khi code đi quá xa, từ đó giảm thời gian sửa ghép ở cuối.

## 7. AI giúp gì / AI sai gì

- **Giúp:** AI hỗ trợ brainstorm rất tốt, đặc biệt khi cần mở rộng ý tưởng, soi thêm các failure mode hoặc gợi ý cách tổ chức SPEC. Khi plan đã rõ ràng, AI cũng hỗ trợ viết code rất nhanh, nhất là các phần boilerplate, SQL/query mẫu và draft nội dung cho slide hoặc tài liệu.
- **Sai/mislead:** AI đôi khi đề xuất kiến trúc hoặc flow nghe có vẻ hợp lý nhưng lại thiếu thực tế triển khai, ví dụ gom quá nhiều chức năng vào một luồng duy nhất, bỏ qua các ràng buộc về dữ liệu thật hoặc gợi ý dùng API/thư viện chưa chắc còn tương thích với version hiện tại. Ngoài ra, AI cũng có xu hướng bỏ sót các edge case khó chịu nếu prompt chỉ mô tả bài toán theo happy path.

