# Báo Cáo Cá Nhân - Hackathon

**Họ và tên:** Phạm Thanh LAm
**Mã sinh viên:** 2A202600491

## 1. Role cụ thể trong nhóm

**System Architect & Core Developer (Kiến trúc sư hệ thống)**
Người trực tiếp đảm nhận vai trò định hình kiến trúc lõi của dự án từ zero. Thay vì chỉ viết tính năng đơn lẻ, tôi thiết lập nền móng kỹ thuật, tiêu chuẩn tích hợp và hệ thống dữ liệu để làm bệ phóng cho các thành viên khác dễ dàng phát triển phần việc của mình.

## 2. Phần phụ trách cụ thể

- **Thiết lập Core Base & Public Database Setup:** Hoàn thiện bộ khung project ban đầu (thư mục, `.env`, dependency). Thiết kế cấu trúc database mock chia sẻ chung thông qua `database.py` và `setup_db.py`. Đảm bảo toàn bộ nhóm sử dụng chung nguồn dữ liệu kết nối ổn định, dễ dàng mock data để test hệ thống.
- **Xây dựng Framework/Template cho Tools:** Định nghĩa kiến trúc cho các chức năng phân mảnh thông qua file `tools.py`. Tạo khung chuẩn cho 12 công cụ (dùng decorator `@tool` của LangChain) giúp các thành viên khác chỉ cần fill logic hàm vào mà không lo bị break cấu trúc luồng của Agent.
- **Viết System Prompt khung cứng (Core Backbone):** Thiết kế cốt lõi của bộ não Agent trong `system_prompt.md`. Định hướng rõ giới hạn quyền hạn nghiêm ngặt, cách thức suy luận ReAct và áp đặt luật bảo mật "phụ huynh nào chỉ xem được thông tin của học sinh đó" ngay tại tầng suy luận gốc.

## 3. SPEC phần nào mạnh nhất, phần nào yếu nhất? Vì sao?

- **Phần mạnh nhất:** Bộ **System Prompt và Tool Routing (Luân chuyển Tools)**. Nhờ đóng khung cứng các nguyên tắc trong prompt cùng thiết lập định dạng schema công cụ rõ ràng, Agent hiểu rất chính xác khi nào cần gọi tool bảng điểm, khi nào trả về lịch học mà gần như không gặp hiện tượng nhầm lẫn tool hay rò rỉ dữ liệu (data leakage) giữa các role.
- **Phần yếu nhất:** Tối ưu hóa **Giao diện hiển thị (UI Rendering)** ở phía frontend. Do dành quá nhiều thời gian làm base architecture backend và tinh chỉnh LLM Prompt, phần hiển thị từ Streamlit chỉ dừng ở mức text cơ bản. Nếu có bảng biểu (dataframe/charts) trực quan cho các thống kê học tập hay điểm danh thì đồ án sẽ thuyết phục hơn thay vì chỉ in ra markdown thô.

## 4. Đóng góp cụ thể khác với mục 2

- **Testing & Debugging chuyên sâu:** Trực tiếp giám sát, bật log chạy ngầm (LangChain trace) để debug các lỗi parse tham số của Agent. Phát hiện và xử lý lỗi khi AI tự ý "đoán" tham số truyền vào tool thay vì dùng tham số thật.
- **Review và Support API:** Hỗ trợ thành viên sửa lỗi kết nối Data, giải quyết các đoạn xung đột Git khi anh em làm chung file config và hướng khắc phục sự cố đọc nhầm biến môi trường khi deploy lên server Streamlit Cloud.

## 5. 1 điều học được trong hackathon mà trước đó chưa biết

Hiểu sâu sắc về luồng hoạt động nội bộ của **LangChain AgentExecutor và nguyên lý ReAct (Reasoning and Acting)**. Ý thức được cách LLM phải tuân theo chu kỳ `Thought -> Action -> Observation -> Final Answer` để gọi hàm. Đặc biệt nhận ra rằng nếu Description của hàm truyền vào (trong docstring của `@tool`) không rõ ràng, AI sẽ chọn sai Action ngay lập tức.

## 6. Nếu làm lại, đổi gì?

Nếu được làm lại khoản base, tôi sẽ **từ bỏ cấu trúc lưu Data dạng file Flat JSON và chuyển thẳng sang thiết lập SQLite Database kết hợp SQLAlchemy**. Lúc đầu dùng file mock up rất nhanh, nhưng khi codebase phình ra và thành viên khác cần thêm bảng lịch sử điểm danh hay lịch sử request thì JSON file handle queries khá lỏng lẻo và dễ bị bug bất đồng bộ trạng thái. Sử dụng database chuẩn với ORM sẽ giúp base chịu tải tốt hơn ở giai đoạn ghép nối.

## 7. AI giúp gì? AI sai/mislead ở đâu?

- **AI giúp ích (Điểm tích cực):** Các công cụ AI (Gemini/Copilot) thực sự vĩ đại trong việc tự động sinh (gen) bộ boilerplate code để bắt đầu project (như gen base cho tool, tạo dump mock data khổng lồ cho hệ thống học sinh/tuition). Ngoài ra, khả năng đọc và tóm tắt lỗi Streamlit/Langchain Traceback giúp tiết kiệm triệt để thời gian tra Google.
- **AI bị lỗi/Mislead (Hạn chế):** Trong quá trình setup Base, AI hay Halucinate việc gợi ý sử dụng các class LangChain đã bị **Deprecated** trong phiên bản cũ do out-of-date knowledge, mất thời gian tự cài đặt và sửa lại namespace. Thêm nữa, khi tối ưu System Prompt, AI thường xuyên khuyên dùng prompt ngắn để tiết kiệm token, điều này "vô tình" cắt bớt các ràng buộc quan trọng (ví dụ quy tắc so khớp user credentials) khiến bộ não ứng dụng mất tính an toàn.
