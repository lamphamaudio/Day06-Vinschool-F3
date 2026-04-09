import psycopg2
from src.config import get_env

def setup_database():
    db_url = get_env("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()

        # 1. Read and run the schema
        print("Applying schema from db_design.sql...")
        with open("src/db_design.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        # We need to drop existing stuff if we want to "reset"
        # Since it's a new schema 'school_ai', we can just drop the schema if it exists
        cursor.execute("DROP SCHEMA IF EXISTS school_ai CASCADE;")
        cursor.execute(schema_sql)

        # 2. Insert Mock Data
        print("Inserting mock data...")
        mock_data_sql = """
        SET search_path TO school_ai, public;

        -- Insert Teachers
        INSERT INTO teachers (id, teacher_code, full_name, department, subject_specialty) VALUES 
        ('11111111-1111-1111-1111-111111111111', 'GV001', 'Cô Trần Thị B', 'Toán học', 'Toán'),
        ('11111111-1111-1111-1111-222222222222', 'GV002', 'Thầy Nguyễn Văn C', 'Vật lý', 'Lý');

        -- Insert Classes
        INSERT INTO classes (id, class_code, class_name, grade_level, school_year, homeroom_teacher_id) VALUES 
        ('22222222-2222-2222-2222-222222222222', '10A1', 'Lớp 10A1', '10', '2023-2024', '11111111-1111-1111-1111-111111111111'),
        ('22222222-2222-2222-2222-333333333333', '10A2', 'Lớp 10A2', '10', '2023-2024', '11111111-1111-1111-1111-222222222222');

        -- Insert Parents
        INSERT INTO parents (id, parent_code, full_name, email, password_hash) VALUES 
        ('44444444-4444-4444-4444-444444444444', 'PH001', 'Nguyễn Văn A', 'parentA@example.com', '123456'),
        ('44444444-4444-4444-4444-555555555555', 'PH002', 'Lê Thị B', 'parentB@example.com', '123456');

        -- Insert Students
        INSERT INTO students (id, student_code, full_name, class_id) VALUES 
        ('33333333-3333-3333-3333-333333333333', 'HS001', 'Nguyễn Văn Con', '22222222-2222-2222-2222-222222222222'),
        ('33333333-3333-3333-3333-444444444444', 'HS002', 'Nguyễn Thị Bé', '22222222-2222-2222-2222-222222222222'),
        ('33333333-3333-3333-3333-555555555555', 'HS003', 'Lê Văn C', '22222222-2222-2222-2222-333333333333');

        -- Link Parent 1 to HS001 and HS002 (Multiple children)
        INSERT INTO parent_student_links (parent_id, student_id, relationship, is_primary) VALUES 
        ('44444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', 'father', TRUE),
        ('44444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-444444444444', 'father', FALSE);

        -- Link Parent 2 to HS003
        INSERT INTO parent_student_links (parent_id, student_id, relationship, is_primary) VALUES 
        ('44444444-4444-4444-4444-555555555555', '33333333-3333-3333-3333-555555555555', 'mother', TRUE);

        -- Insert Subjects
        INSERT INTO subjects (id, subject_code, subject_name) VALUES 
        ('55555555-5555-5555-5555-555555555555', 'MATH', 'Toán'),
        ('66666666-6666-6666-6666-666666666666', 'PHYS', 'Vật lý'),
        ('77777777-7777-7777-7777-777777777777', 'ENGL', 'Tiếng Anh');

        -- Schedule for 10A1 (HS001, HS002)
        INSERT INTO schedules (class_id, subject_id, teacher_id, day_of_week, period_no) VALUES
        ('22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', 4, 1),
        ('22222222-2222-2222-2222-222222222222', '66666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111', 4, 2);

        -- Attendance
        INSERT INTO attendance_records (student_id, attendance_date, status, note) VALUES
        ('33333333-3333-3333-3333-333333333333', CURRENT_DATE, 'present', NULL),
        ('33333333-3333-3333-3333-444444444444', CURRENT_DATE, 'absent', 'Nghỉ ốm có phép'),
        ('33333333-3333-3333-3333-555555555555', CURRENT_DATE, 'late', 'Kẹt xe');

        -- Grades
        INSERT INTO grade_records (student_id, subject_id, assessment_name, score) VALUES
        ('33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555555', 'Kết quả học kỳ 1', 9.5),
        ('33333333-3333-3333-3333-444444444444', '55555555-5555-5555-5555-555555555555', 'Kiểm tra miệng', 4.0),
        ('33333333-3333-3333-3333-555555555555', '77777777-7777-7777-7777-777777777777', 'Thi giữa kỳ', 7.0);

        -- Teacher Comments
        INSERT INTO teacher_daily_comments (student_id, teacher_id, subject_id, comment_date, comment_text) VALUES
        ('33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555555', CURRENT_DATE, 'Học sinh rất năng nổ xây dựng bài.'),
        ('33333333-3333-3333-3333-444444444444', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555555', CURRENT_DATE, 'Cần chú ý ôn tập kỹ hơn phần phân số.');

        -- Announcements
        INSERT INTO school_announcements (title, content, category) VALUES
        ('Thông báo Họp Phụ huynh', 'Chào mừng quý phụ huynh đến họp vào chủ nhật tuần này.', 'meeting'),
        ('Nghỉ lễ Giỗ tổ Hùng Vương', 'Trường nghỉ ngày 10/3 Âm lịch.', 'event');

        -- Fees
        INSERT INTO fee_records (student_id, fee_name, fee_type, amount, due_date, status) VALUES
        ('33333333-3333-3333-3333-333333333333', 'Học phí Ký túc xá', 'tuition', 2000000, CURRENT_DATE + INTERVAL '5 days', 'pending'),
        ('33333333-3333-3333-3333-444444444444', 'Phí xe bus Th4', 'tuition', 800000, CURRENT_DATE - INTERVAL '2 days', 'overdue'),
        ('33333333-3333-3333-3333-555555555555', 'Học phí Th4', 'tuition', 5000000, CURRENT_DATE + INTERVAL '15 days', 'paid');
        """
        cursor.execute(mock_data_sql)
        print("Database setup successfully!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == "__main__":
    setup_database()
