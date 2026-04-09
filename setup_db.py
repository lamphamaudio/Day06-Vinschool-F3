import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    db_url = os.getenv("DATABASE_URL")
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

        -- Insert Teacher
        INSERT INTO teachers (id, teacher_code, full_name, department, subject_specialty)
        VALUES ('11111111-1111-1111-1111-111111111111', 'GV001', 'Cô Trần Thị B', 'Toán học', 'Toán');

        -- Insert Class
        INSERT INTO classes (id, class_code, class_name, grade_level, school_year, homeroom_teacher_id)
        VALUES ('22222222-2222-2222-2222-222222222222', '10A1', 'Lớp 10A1', '10', '2023-2024', '11111111-1111-1111-1111-111111111111');

        -- Insert Student
        INSERT INTO students (id, student_code, full_name, class_id)
        VALUES ('33333333-3333-3333-3333-333333333333', 'HS001', 'Nguyễn Văn Con', '22222222-2222-2222-2222-222222222222');

        -- Insert Parent
        INSERT INTO parents (id, parent_code, full_name, email, password_hash)
        VALUES ('44444444-4444-4444-4444-444444444444', 'PH001', 'Nguyễn Văn A', 'parentA@example.com', '123456');

        -- Link Parent and Student
        INSERT INTO parent_student_links (parent_id, student_id, relationship, is_primary)
        VALUES ('44444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', 'father', TRUE);

        -- Insert Subjects
        INSERT INTO subjects (id, subject_code, subject_name) VALUES 
        ('55555555-5555-5555-5555-555555555555', 'MATH', 'Toán'),
        ('66666666-6666-6666-6666-666666666666', 'PHYS', 'Vật lý');

        -- Insert Schedule
        INSERT INTO schedules (class_id, subject_id, teacher_id, day_of_week, period_no) VALUES
        ('22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', 4, 1),
        ('22222222-2222-2222-2222-222222222222', '66666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111', 4, 2);

        -- Insert Attendance
        INSERT INTO attendance_records (student_id, attendance_date, status) VALUES
        ('33333333-3333-3333-3333-333333333333', CURRENT_DATE, 'present'),
        ('33333333-3333-3333-3333-333333333333', CURRENT_DATE - INTERVAL '1 day', 'present');

        -- Insert Grades
        INSERT INTO grade_records (student_id, subject_id, assessment_name, score) VALUES
        ('33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555555', 'Kiểm tra 15p', 9.0),
        ('33333333-3333-3333-3333-333333333333', '66666666-6666-6666-6666-666666666666', 'Giữa kỳ', 8.5);

        -- Insert Announcements
        INSERT INTO school_announcements (title, content, category) VALUES
        ('Lịch nghỉ lễ', 'Toàn trường nghỉ lễ từ 30/4 đến 3/5', 'event');

        -- Insert Fees
        INSERT INTO fee_records (student_id, fee_name, fee_type, amount, due_date) VALUES
        ('33333333-3333-3333-3333-333333333333', 'Học phí Tháng 4', 'tuition', 5000000, CURRENT_DATE + INTERVAL '10 days');
        """
        cursor.execute(mock_data_sql)
        print("Database setup successfully!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == "__main__":
    setup_database()
