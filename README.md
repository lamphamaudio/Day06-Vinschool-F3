# AI Vin Learner

Ứng dụng Streamlit hỗ trợ phụ huynh tra cứu thông tin học tập của học sinh qua chatbot AI. Dữ liệu được lấy từ PostgreSQL và toàn bộ cấu hình runtime được nạp từ file `.env`.

## Chức năng chính

- Đăng nhập bằng mã phụ huynh hoặc email.
- Tra cứu lịch học, điểm số, điểm danh, học phí và thông báo.
- Sinh câu trả lời AI dựa trên dữ liệu học sinh đang gắn với phiên đăng nhập.
- Ghi log hội thoại vào database.

## Yêu cầu

- Python 3.10+
- PostgreSQL compatible database
- OpenAI API key

## Cấu hình môi trường

Tạo file `.env` ở thư mục gốc project:

```env
DATABASE_URL=postgresql://username:password@host:5432/dbname?sslmode=require
OPENAI_API_KEY=your_openai_api_key
```

Ứng dụng hiện đọc biến môi trường trực tiếp từ `.env`, không còn nhập `OPENAI_API_KEY` trên giao diện Streamlit.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Khởi tạo dữ liệu mẫu

Lệnh dưới đây sẽ tạo schema `school_ai` và nạp dữ liệu mẫu:

```bash
python3 setup_db.py
```

## Chạy ứng dụng

```bash
streamlit run src/app.py
```

Sau khi chạy, mở giao diện Streamlit trong trình duyệt theo URL mà terminal cung cấp.

## Tài khoản mẫu

- Phụ huynh: `PH001`
- Hoặc email: `parentA@example.com`
- Mật khẩu: `123456`

## Cấu trúc chính

- [src/app.py](/Users/quanliver/Projects/AI_Vin_Learner/Day06-2A202600491/src/app.py): giao diện Streamlit và luồng đăng nhập/chat.
- [src/agent.py](/Users/quanliver/Projects/AI_Vin_Learner/Day06-2A202600491/src/agent.py): định tuyến intent và gọi OpenAI.
- [src/database.py](/Users/quanliver/Projects/AI_Vin_Learner/Day06-2A202600491/src/database.py): truy vấn database và connection pool.
- [src/config.py](/Users/quanliver/Projects/AI_Vin_Learner/Day06-2A202600491/src/config.py): nạp biến môi trường từ `.env`.
- [setup_db.py](/Users/quanliver/Projects/AI_Vin_Learner/Day06-2A202600491/setup_db.py): tạo schema và seed dữ liệu mẫu.

## Lưu ý

- Nếu database dùng chế độ sleep/cold start, truy vấn đầu tiên có thể chậm khoảng 10-15 giây.

