-- Mock data for school_ai schema
-- Run this file after docs/db_design.sql has been applied.

BEGIN;

SET search_path TO school_ai, public;

-- Teachers
INSERT INTO teachers (
    id, teacher_code, full_name, phone, email, department, subject_specialty, role_name, is_active
) VALUES
    ('10000000-0000-0000-0000-000000000001', 'GV001', 'Tran Thi Bich', '0901000001', 'bich.tran@school.local', 'Mathematics', 'Toan', 'Homeroom Teacher', TRUE),
    ('10000000-0000-0000-0000-000000000002', 'GV002', 'Nguyen Hoang Long', '0901000002', 'long.nguyen@school.local', 'Science', 'Vat ly', 'Subject Teacher', TRUE),
    ('10000000-0000-0000-0000-000000000003', 'GV003', 'Pham Thu Ha', '0901000003', 'ha.pham@school.local', 'Languages', 'Tieng Anh', 'Subject Teacher', TRUE),
    ('10000000-0000-0000-0000-000000000004', 'GV004', 'Le Minh Chau', '0901000004', 'chau.le@school.local', 'Student Affairs', 'Counseling', 'Counselor', TRUE),
    ('10000000-0000-0000-0000-000000000005', 'GV005', 'Vo Quoc An', '0901000005', 'an.vo@school.local', 'Technology', 'Tin hoc', 'Subject Teacher', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Classes
INSERT INTO classes (
    id, class_code, class_name, grade_level, school_year, homeroom_teacher_id
) VALUES
    ('20000000-0000-0000-0000-000000000001', '10A1', 'Lop 10A1', '10', '2025-2026', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000002', '08B1', 'Lop 8B1', '8', '2025-2026', '10000000-0000-0000-0000-000000000004')
ON CONFLICT (id) DO NOTHING;

-- Parents
INSERT INTO parents (
    id, parent_code, full_name, phone, email, password_hash, status, last_login_at
) VALUES
    ('40000000-0000-0000-0000-000000000001', 'PH001', 'Nguyen Van An', '0912000001', 'parentA@example.com', '123456', 'active', NOW() - INTERVAL '2 hours'),
    ('40000000-0000-0000-0000-000000000002', 'PH002', 'Tran Thi Lan', '0912000002', 'parentB@example.com', '123456', 'active', NOW() - INTERVAL '1 day'),
    ('40000000-0000-0000-0000-000000000003', 'PH003', 'Le Quang Minh', '0912000003', 'parentC@example.com', '123456', 'active', NOW() - INTERVAL '3 days')
ON CONFLICT (id) DO NOTHING;

-- Students
INSERT INTO students (
    id, student_code, full_name, date_of_birth, gender, class_id, enrollment_status
) VALUES
    ('30000000-0000-0000-0000-000000000001', 'HS001', 'Nguyen Minh Khang', DATE '2010-09-12', 'male', '20000000-0000-0000-0000-000000000001', 'active'),
    ('30000000-0000-0000-0000-000000000002', 'HS002', 'Nguyen Gia Han', DATE '2010-11-03', 'female', '20000000-0000-0000-0000-000000000001', 'active'),
    ('30000000-0000-0000-0000-000000000003', 'HS003', 'Le Bao Chau', DATE '2012-05-21', 'female', '20000000-0000-0000-0000-000000000002', 'active')
ON CONFLICT (id) DO NOTHING;

-- Parent-student links
INSERT INTO parent_student_links (
    id, parent_id, student_id, relationship, is_primary
) VALUES
    ('41000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'father', TRUE),
    ('41000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', 'mother', FALSE),
    ('41000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', 'father', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Subjects
INSERT INTO subjects (
    id, subject_code, subject_name
) VALUES
    ('50000000-0000-0000-0000-000000000001', 'MATH', 'Toan'),
    ('50000000-0000-0000-0000-000000000002', 'PHYS', 'Vat ly'),
    ('50000000-0000-0000-0000-000000000003', 'ENG', 'Tieng Anh'),
    ('50000000-0000-0000-0000-000000000004', 'LIT', 'Ngu van'),
    ('50000000-0000-0000-0000-000000000005', 'IT', 'Tin hoc'),
    ('50000000-0000-0000-0000-000000000006', 'LIFE', 'Ky nang song')
ON CONFLICT (id) DO NOTHING;

-- Student enrollments by subject
INSERT INTO student_subjects (
    id, student_id, subject_id, teacher_id, semester, school_year
) VALUES
    ('60000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'HK2', '2025-2026'),
    ('60000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'HK2', '2025-2026'),
    ('60000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'HK2', '2025-2026'),
    ('60000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000005', 'HK2', '2025-2026'),
    ('60000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000002', '50000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'HK2', '2025-2026'),
    ('60000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'HK2', '2025-2026')
ON CONFLICT (id) DO NOTHING;

-- Attendance records
INSERT INTO attendance_records (
    id, student_id, attendance_date, status, note, recorded_by
) VALUES
    ('70000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', CURRENT_DATE - 6, 'present', NULL, '10000000-0000-0000-0000-000000000001'),
    ('70000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'present', NULL, '10000000-0000-0000-0000-000000000001'),
    ('70000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', CURRENT_DATE - 4, 'late', 'Den lop muon 10 phut vi tac duong.', '10000000-0000-0000-0000-000000000001'),
    ('70000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000001', CURRENT_DATE - 3, 'present', NULL, '10000000-0000-0000-0000-000000000001'),
    ('70000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000001', CURRENT_DATE - 2, 'present', NULL, '10000000-0000-0000-0000-000000000001'),
    ('70000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000001', CURRENT_DATE - 1, 'absent', 'Xin nghi co phep do kham suc khoe dinh ky.', '10000000-0000-0000-0000-000000000004'),
    ('70000000-0000-0000-0000-000000000007', '30000000-0000-0000-0000-000000000001', CURRENT_DATE, 'present', NULL, '10000000-0000-0000-0000-000000000001'),
    ('70000000-0000-0000-0000-000000000008', '30000000-0000-0000-0000-000000000003', CURRENT_DATE - 2, 'present', NULL, '10000000-0000-0000-0000-000000000004'),
    ('70000000-0000-0000-0000-000000000009', '30000000-0000-0000-0000-000000000003', CURRENT_DATE - 1, 'present', NULL, '10000000-0000-0000-0000-000000000004'),
    ('70000000-0000-0000-0000-000000000010', '30000000-0000-0000-0000-000000000003', CURRENT_DATE, 'present', NULL, '10000000-0000-0000-0000-000000000004')
ON CONFLICT (id) DO NOTHING;

-- Grade records
INSERT INTO grade_records (
    id, student_id, subject_id, teacher_id, assessment_name, assessment_type, score, max_score, recorded_at, note
) VALUES
    ('80000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'Kiem tra 15 phut lan 1', 'quiz', 8.50, 10, NOW() - INTERVAL '15 days', 'Tinh toan can than, trinh bay ro rang.'),
    ('80000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'Giua ky HK2', 'midterm', 8.80, 10, NOW() - INTERVAL '8 days', 'Lam bai tot, can chu y them cau hinh hoc.'),
    ('80000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'Thuc hanh thi nghiem', 'practical', 9.20, 10, NOW() - INTERVAL '7 days', 'Thao tac phong thi nghiem an toan va chinh xac.'),
    ('80000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'Speaking Test', 'oral', 8.10, 10, NOW() - INTERVAL '5 days', 'Phat am tot, tu tin hon so voi dau hoc ky.'),
    ('80000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000005', 'Du an PowerPoint', 'project', 9.00, 10, NOW() - INTERVAL '3 days', 'Noi dung day du, trinh bay dep.'),
    ('80000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'Quiz Unit 8', 'quiz', 9.40, 10, NOW() - INTERVAL '4 days', 'Nho tu vung tot va phan xa nhanh.')
ON CONFLICT (id) DO NOTHING;

-- Daily teacher comments
INSERT INTO teacher_daily_comments (
    id, student_id, teacher_id, subject_id, comment_date, comment_text, tone_label
) VALUES
    ('90000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'Khang chu dong phat bieu trong gio Toan va ho tro ban cung nhom rat tot.', 'positive'),
    ('90000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000003', CURRENT_DATE - 3, 'Con da tu tin hon khi thuyet trinh bang tieng Anh, can tiep tuc ren phat am cuoi cau.', 'encouraging'),
    ('90000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000004', NULL, CURRENT_DATE - 1, 'Thai do hoc tap on dinh, con hop tac tot va ton trong noi quy lop hoc.', 'positive'),
    ('90000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004', NULL, CURRENT_DATE - 2, 'Bao Chau hoan thanh bai tap dung han va co tinh than giup do ban be.', 'positive')
ON CONFLICT (id) DO NOTHING;

-- Stored summaries
INSERT INTO report_summaries (
    id, student_id, summary_type, generated_by_parent_id, summary_text, source_from_date, source_to_date
) VALUES
    ('91000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'weekly', '40000000-0000-0000-0000-000000000001', 'Trong tuan qua, Khang duy tri nen nep hoc tap tot, ket qua Toan va Tin hoc on dinh, can tiep tuc dieu chinh thoi gian den lop de tranh di muon.', CURRENT_DATE - 7, CURRENT_DATE),
    ('91000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000003', 'monthly', '40000000-0000-0000-0000-000000000003', 'Bao Chau co tien bo ro trong mon Tieng Anh, thai do hoc tap tich cuc va chuyen can on dinh trong thang.', CURRENT_DATE - 30, CURRENT_DATE)
ON CONFLICT (id) DO NOTHING;

-- Weekly schedule
INSERT INTO schedules (
    id, class_id, subject_id, teacher_id, day_of_week, period_no, room_name, effective_from, effective_to
) VALUES
    ('b0000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 1, 1, 'P.301', DATE '2025-09-01', NULL),
    ('b0000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 1, 2, 'P.302', DATE '2025-09-01', NULL),
    ('b0000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 2, 1, 'Lab 1', DATE '2025-09-01', NULL),
    ('b0000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000005', 2, 3, 'Computer 2', DATE '2025-09-01', NULL),
    ('b0000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000004', 3, 2, 'P.305', DATE '2025-09-01', NULL),
    ('b0000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000004', 5, 4, 'Hall A', DATE '2025-09-01', NULL),
    ('b0000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000002', '50000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 1, 1, 'P.201', DATE '2025-09-01', NULL)
ON CONFLICT (id) DO NOTHING;

-- Menus
INSERT INTO menus (
    id, menu_date, meal_type, item_name, notes
) VALUES
    ('c0000000-0000-0000-0000-000000000001', CURRENT_DATE, 'lunch', 'Com ga nuong, canh rau cu, dua hau', 'Khau phan tieu chuan khoi THPT'),
    ('c0000000-0000-0000-0000-000000000002', CURRENT_DATE, 'snack', 'Sua tuoi va banh mi mem', NULL),
    ('c0000000-0000-0000-0000-000000000003', CURRENT_DATE + 1, 'lunch', 'Bun bo, cha gio, chuoi', 'Tang cuong rau xanh'),
    ('c0000000-0000-0000-0000-000000000004', CURRENT_DATE + 1, 'snack', 'Sua chua va banh quy', NULL)
ON CONFLICT (id) DO NOTHING;

-- Announcements
INSERT INTO school_announcements (
    id, title, content, category, audience_scope, published_at, effective_from, effective_to, created_by
) VALUES
    ('d0000000-0000-0000-0000-000000000001', 'Thong bao lich hop phu huynh cuoi ky', 'Nha truong to chuc hop phu huynh vao 08:00 thu Bay tuan nay tai hoi truong lon.', 'meeting', 'all', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days', NOW() + INTERVAL '5 days', '10000000-0000-0000-0000-000000000004'),
    ('d0000000-0000-0000-0000-000000000002', 'Dieu chinh lich kiem tra Vat ly', 'Bai kiem tra Vat ly khoi 10 duoc chuyen sang tiet 2 ngay thu Nam tuan sau.', 'schedule_change', 'grade_10', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day', NOW() + INTERVAL '6 days', '10000000-0000-0000-0000-000000000002'),
    ('d0000000-0000-0000-0000-000000000003', 'Nhac han hoc phi thang 04', 'Quy phu huynh vui long hoan thanh hoc phi truoc ngay den han de he thong cap nhat trang thai dung han.', 'tuition', 'all', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days', NOW() + INTERVAL '7 days', '10000000-0000-0000-0000-000000000004'),
    ('d0000000-0000-0000-0000-000000000004', 'Ngay hoi STEM cap truong', 'Hoc sinh khoi 8 va khoi 10 se tham gia ngay hoi STEM vao chieu thu Sau tai san truong chinh.', 'event', 'selected_classes', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours', NOW() + INTERVAL '10 days', '10000000-0000-0000-0000-000000000005')
ON CONFLICT (id) DO NOTHING;

-- Announcement targets
INSERT INTO announcement_targets (
    id, announcement_id, class_id, student_id
) VALUES
    ('e0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', NULL),
    ('e0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000001', NULL),
    ('e0000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000002', NULL)
ON CONFLICT (id) DO NOTHING;

-- Fee records
INSERT INTO fee_records (
    id, student_id, fee_name, fee_type, amount, currency_code, due_date, status, payment_reference, payment_url, qr_code_url, last_synced_at
) VALUES
    ('f0000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'Hoc phi thang 04/2026', 'tuition', 12500000, 'VND', CURRENT_DATE + 5, 'pending', 'PAY-APR-001', 'https://payments.school.local/invoice/PAY-APR-001', 'https://payments.school.local/qr/PAY-APR-001', NOW() - INTERVAL '2 hours'),
    ('f0000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', 'Phi ban tru thang 03/2026', 'meal', 1800000, 'VND', CURRENT_DATE - 10, 'paid', 'PAY-MAR-015', 'https://payments.school.local/invoice/PAY-MAR-015', 'https://payments.school.local/qr/PAY-MAR-015', NOW() - INTERVAL '1 day'),
    ('f0000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', 'Hoc phi thang 04/2026', 'tuition', 9800000, 'VND', CURRENT_DATE - 2, 'overdue', 'PAY-APR-099', 'https://payments.school.local/invoice/PAY-APR-099', 'https://payments.school.local/qr/PAY-APR-099', NOW() - INTERVAL '3 hours')
ON CONFLICT (id) DO NOTHING;

-- Chat session history
INSERT INTO chat_sessions (
    id, parent_id, student_id, channel, status, started_at, ended_at, last_activity_at
) VALUES
    ('11000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'web', 'ended', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '15 minutes', NOW() - INTERVAL '2 days' + INTERVAL '15 minutes'),
    ('11000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', 'chat', 'active', NOW() - INTERVAL '4 hours', NULL, NOW() - INTERVAL '30 minutes')
ON CONFLICT (id) DO NOTHING;

-- Chat messages
INSERT INTO chat_messages (
    id, session_id, sender, message_text, intent_name, confidence_score, created_at
) VALUES
    ('12000000-0000-0000-0000-000000000001', '11000000-0000-0000-0000-000000000001', 'parent', 'Hom nay con hoc mon gi?', 'SCHEDULE', 0.9825, NOW() - INTERVAL '2 days' + INTERVAL '2 minutes'),
    ('12000000-0000-0000-0000-000000000002', '11000000-0000-0000-0000-000000000001', 'assistant', 'Hom nay Khang co Toan, Tieng Anh va Tin hoc theo thoi khoa bieu lop 10A1.', 'SCHEDULE', 0.9825, NOW() - INTERVAL '2 days' + INTERVAL '3 minutes'),
    ('12000000-0000-0000-0000-000000000003', '11000000-0000-0000-0000-000000000002', 'parent', 'Hoc phi thang nay da thanh toan chua?', 'TUITION', 0.9710, NOW() - INTERVAL '55 minutes'),
    ('12000000-0000-0000-0000-000000000004', '11000000-0000-0000-0000-000000000002', 'assistant', 'Hoc phi thang 04/2026 cua Bao Chau dang o trang thai overdue.', 'TUITION', 0.9710, NOW() - INTERVAL '53 minutes')
ON CONFLICT (id) DO NOTHING;

-- AI audit logs
INSERT INTO ai_audit_logs (
    id, session_id, message_id, parent_id, student_id, question_text, answer_text, intent_name, data_sources, data_freshness_at, model_name, confidence_label, was_escalated, created_at
) VALUES
    ('13000000-0000-0000-0000-000000000001', '11000000-0000-0000-0000-000000000001', '12000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'Hom nay con hoc mon gi?', 'Hom nay Khang co Toan, Tieng Anh va Tin hoc theo thoi khoa bieu lop 10A1.', 'SCHEDULE', '["schedules"]'::jsonb, NOW() - INTERVAL '2 days' + INTERVAL '3 minutes', 'gpt-4o-mini', 'high', FALSE, NOW() - INTERVAL '2 days' + INTERVAL '3 minutes'),
    ('13000000-0000-0000-0000-000000000002', '11000000-0000-0000-0000-000000000002', '12000000-0000-0000-0000-000000000004', '40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', 'Hoc phi thang nay da thanh toan chua?', 'Hoc phi thang 04/2026 cua Bao Chau dang o trang thai overdue.', 'TUITION', '["fee_records"]'::jsonb, NOW() - INTERVAL '53 minutes', 'gpt-4o-mini', 'high', FALSE, NOW() - INTERVAL '53 minutes')
ON CONFLICT (id) DO NOTHING;

-- Correction logs
INSERT INTO correction_logs (
    id, session_id, parent_id, student_id, message_id, correction_type, original_value, corrected_value, notes, created_at
) VALUES
    ('14000000-0000-0000-0000-000000000001', '11000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '12000000-0000-0000-0000-000000000002', 'schedule_room_update', 'Phong P.302', 'Phong P.303', 'Phu huynh thong bao lop hoc Tieng Anh da doi phong tu dau tuan.', NOW() - INTERVAL '2 days' + INTERVAL '5 minutes')
ON CONFLICT (id) DO NOTHING;

-- Support tickets
INSERT INTO support_tickets (
    id, ticket_code, parent_id, student_id, assigned_teacher_id, category, priority, status, title, description, source_session_id, created_at, updated_at, resolved_at
) VALUES
    ('15000000-0000-0000-0000-000000000001', 'TK-20260401001', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'academic_concern', 'medium', 'resolved', 'Trao doi ve viec di muon trong tuan', 'Phu huynh muon nho giao vien chu nhiem phoi hop nhac nho hoc sinh sap xep thoi gian di hoc dung gio.', '11000000-0000-0000-0000-000000000001', NOW() - INTERVAL '6 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
    ('15000000-0000-0000-0000-000000000002', 'TK-20260409001', '40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004', 'fee_issue', 'high', 'open', 'Can ho tro hoc phi qua han', 'Phu huynh can duoc huong dan cach thanh toan hoc phi qua han va xac nhan cap nhat sau khi chuyen khoan.', '11000000-0000-0000-0000-000000000002', NOW() - INTERVAL '20 minutes', NOW() - INTERVAL '20 minutes', NULL)
ON CONFLICT (id) DO NOTHING;

-- Notifications pushed to parents
INSERT INTO parent_notifications (
    id, parent_id, student_id, announcement_id, title, content, category, is_read, delivered_at, read_at
) VALUES
    ('16000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Thong bao hop phu huynh cuoi ky', 'Hop phu huynh du kien dien ra vao 08:00 thu Bay tai hoi truong lon.', 'meeting', TRUE, NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 day'),
    ('16000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'Dieu chinh lich kiem tra Vat ly', 'Lich kiem tra Vat ly cua lop 10A1 da doi sang thu Nam tiet 2.', 'schedule_change', FALSE, NOW() - INTERVAL '1 day', NULL),
    ('16000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-000000000003', 'Nhac han hoc phi thang 04', 'Hoc phi thang 04/2026 dang qua han, vui long thanh toan som de tranh anh huong den doi soat.', 'tuition', FALSE, NOW() - INTERVAL '12 hours', NULL)
ON CONFLICT (id) DO NOTHING;

COMMIT;
