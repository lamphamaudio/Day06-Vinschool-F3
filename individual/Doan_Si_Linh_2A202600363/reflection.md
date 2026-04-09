# Individual reflection — Đoàn Sĩ Linh (2A202600363)

## 1. Role
- Phụ trách phát triển tool tra cứu thông báo từ nhà trường.
- Viết phần Trust trong tài liệu SPEC.

## 2. Đóng góp cụ thể
- Xây dựng và tích hợp tool lấy thông báo của nhà trường, đảm bảo truy xuất đúng nội dung cần thiết để chatbot phản hồi nhất quán.
- Viết và định nghĩa phần Trust trong SPEC: khi AI có thể sai, cơ chế cảnh báo, cách người dùng kiểm tra lại và chỉnh sửa đầu ra.

## 3. SPEC mạnh/yếu
- **Mạnh nhất:** Đưa ra được nhiều case trong phần Trust của SPEC.
- **Yếu nhất:** Một số default behavior trong các tình huống biên chưa được mô tả đủ rõ.

## 4. Đóng góp khác
- Tham gia test và tinh chỉnh prompt để câu trả lời từ tool thông báo rõ ràng, dễ hiểu, đúng giọng điệu sản phẩm.
- Hỗ trợ rà soát và tinh chỉnh luồng xử lý lỗi khi tool thất bại hoặc API timeout để trải nghiệm người dùng ổn định hơn.

## 5. Điều học được
- Trước đây nghĩ chỉ cần nối API vào chatbot là đủ. Khi trực tiếp làm phần Trust và tool thông báo thì hiểu rằng phần quan trọng là cách hệ thống phản hồi khi dữ liệu thiếu/sai: cần minh bạch nguồn, nêu rõ mức chắc chắn của câu trả lời và cho người dùng cách kiểm tra lại. Chất lượng trải nghiệm người dùng không chỉ nằm ở việc tool chạy được mà còn ở cách xử lý các trường hợp không hoàn hảo.

## 6. Nếu làm lại
- Dành thêm thời gian từ sớm để chuẩn hóa các case cho phần thông báo (không có thông báo mới, dữ liệu trùng lặp, thông báo thiếu ngày/nguồn) và định nghĩa rõ default behavior trong SPEC để team triển khai đồng nhất hơn.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI hỗ trợ brainstorm nhanh các tình huống rủi ro trong Trust, gợi ý checklist để rà soát phản hồi và hỗ trợ tạo dữ liệu mẫu để test tool thông báo.
- **Sai/mislead:** AI đôi khi đề xuất luồng quá lý tưởng hoặc quá phức tạp so với phạm vi hackathon, nên vẫn phải chủ động rút gọn và tinh chỉnh để phù hợp với thực tế triển khai.
