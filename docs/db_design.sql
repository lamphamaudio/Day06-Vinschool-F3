-- PostgreSQL schema for the parent-school AI assistant MVP
-- Based on the product scope defined in spec-template.md

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS school_ai;

SET search_path TO school_ai, public;

-- Enums
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'locked');
CREATE TYPE relationship_type AS ENUM ('father', 'mother', 'guardian', 'other');
CREATE TYPE attendance_status AS ENUM ('present', 'absent', 'late', 'excused');
CREATE TYPE fee_status AS ENUM ('pending', 'paid', 'overdue', 'cancelled');
CREATE TYPE sender_type AS ENUM ('parent', 'assistant', 'teacher', 'system');
CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'resolved', 'closed');
CREATE TYPE ticket_priority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE ticket_category AS ENUM (
    'wrong_information',
    'academic_concern',
    'behavior_concern',
    'fee_issue',
    'schedule_issue',
    'general_support'
);
CREATE TYPE notification_category AS ENUM (
    'exam',
    'meeting',
    'tuition',
    'event',
    'schedule_change',
    'general'
);
CREATE TYPE session_channel AS ENUM ('web', 'mobile', 'chat');
CREATE TYPE session_status AS ENUM ('active', 'ended', 'expired');
CREATE TYPE summary_type AS ENUM ('weekly', 'monthly', 'on_demand');

-- Parent accounts
CREATE TABLE parents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    phone TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    status user_status NOT NULL DEFAULT 'active',
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Teachers
CREATE TABLE teachers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT UNIQUE,
    department TEXT,
    subject_specialty TEXT,
    role_name TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Classes
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_code TEXT NOT NULL UNIQUE,
    class_name TEXT NOT NULL,
    grade_level TEXT NOT NULL,
    school_year TEXT NOT NULL,
    homeroom_teacher_id UUID REFERENCES teachers(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Students
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT,
    class_id UUID REFERENCES classes(id),
    enrollment_status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Mapping between parent accounts and students
CREATE TABLE parent_student_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    relationship relationship_type NOT NULL DEFAULT 'guardian',
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (parent_id, student_id)
);

-- Subjects
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_code TEXT NOT NULL UNIQUE,
    subject_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Student enrollment by subject/teacher
CREATE TABLE student_subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id),
    teacher_id UUID REFERENCES teachers(id),
    semester TEXT NOT NULL,
    school_year TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, subject_id, semester, school_year)
);

-- Attendance data
CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    status attendance_status NOT NULL,
    note TEXT,
    recorded_by UUID REFERENCES teachers(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, attendance_date)
);

-- Scores / grades
CREATE TABLE grade_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id),
    teacher_id UUID REFERENCES teachers(id),
    assessment_name TEXT NOT NULL,
    assessment_type TEXT,
    score NUMERIC(5,2) NOT NULL CHECK (score >= 0),
    max_score NUMERIC(5,2) NOT NULL DEFAULT 10 CHECK (max_score > 0),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    note TEXT
);

-- Daily teacher comments used for respectful AI summaries
CREATE TABLE teacher_daily_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES teachers(id),
    subject_id UUID REFERENCES subjects(id),
    comment_date DATE NOT NULL,
    comment_text TEXT NOT NULL,
    tone_label TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- AI-generated summaries stored for audit and reuse
CREATE TABLE report_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    summary_type summary_type NOT NULL,
    generated_by_parent_id UUID REFERENCES parents(id),
    summary_text TEXT NOT NULL,
    source_from_date DATE,
    source_to_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Class schedule
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id),
    teacher_id UUID REFERENCES teachers(id),
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    period_no SMALLINT NOT NULL CHECK (period_no > 0),
    room_name TEXT,
    effective_from DATE,
    effective_to DATE
);

-- Cafeteria / menu data
CREATE TABLE menus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_date DATE NOT NULL,
    meal_type TEXT NOT NULL,
    item_name TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Official school announcements
CREATE TABLE school_announcements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category notification_category NOT NULL DEFAULT 'general',
    audience_scope TEXT NOT NULL DEFAULT 'all',
    published_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_from TIMESTAMPTZ,
    effective_to TIMESTAMPTZ,
    created_by UUID REFERENCES teachers(id)
);

-- Optional mapping announcements to specific classes or students
CREATE TABLE announcement_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    announcement_id UUID NOT NULL REFERENCES school_announcements(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    CHECK (class_id IS NOT NULL OR student_id IS NOT NULL)
);

-- Tuition / fee information
CREATE TABLE fee_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    fee_name TEXT NOT NULL,
    fee_type TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    currency_code CHAR(3) NOT NULL DEFAULT 'VND',
    due_date DATE,
    status fee_status NOT NULL DEFAULT 'pending',
    payment_reference TEXT,
    payment_url TEXT,
    qr_code_url TEXT,
    last_synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chat sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id),
    channel session_channel NOT NULL DEFAULT 'web',
    status session_status NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chat messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender sender_type NOT NULL,
    message_text TEXT NOT NULL,
    intent_name TEXT,
    confidence_score NUMERIC(5,4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Audit log for each AI answer
CREATE TABLE ai_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_id UUID REFERENCES chat_messages(id) ON DELETE SET NULL,
    parent_id UUID NOT NULL REFERENCES parents(id),
    student_id UUID NOT NULL REFERENCES students(id),
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    intent_name TEXT,
    data_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    data_freshness_at TIMESTAMPTZ,
    model_name TEXT,
    confidence_label TEXT,
    was_escalated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User correction signals
CREATE TABLE correction_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    parent_id UUID NOT NULL REFERENCES parents(id),
    student_id UUID NOT NULL REFERENCES students(id),
    message_id UUID REFERENCES chat_messages(id) ON DELETE SET NULL,
    correction_type TEXT NOT NULL,
    original_value TEXT,
    corrected_value TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tickets for escalation to teachers or support staff
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_code TEXT NOT NULL UNIQUE,
    parent_id UUID NOT NULL REFERENCES parents(id),
    student_id UUID NOT NULL REFERENCES students(id),
    assigned_teacher_id UUID REFERENCES teachers(id),
    category ticket_category NOT NULL,
    priority ticket_priority NOT NULL DEFAULT 'medium',
    status ticket_status NOT NULL DEFAULT 'open',
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    source_session_id UUID REFERENCES chat_sessions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- Notifications delivered to parents
CREATE TABLE parent_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    announcement_id UUID REFERENCES school_announcements(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category notification_category NOT NULL DEFAULT 'general',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    delivered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at TIMESTAMPTZ
);

-- Helpful indexes
CREATE INDEX idx_students_class_id ON students(class_id);
CREATE INDEX idx_parent_student_links_parent_id ON parent_student_links(parent_id);
CREATE INDEX idx_parent_student_links_student_id ON parent_student_links(student_id);
CREATE INDEX idx_student_subjects_student_id ON student_subjects(student_id);
CREATE INDEX idx_attendance_records_student_date ON attendance_records(student_id, attendance_date DESC);
CREATE INDEX idx_grade_records_student_recorded_at ON grade_records(student_id, recorded_at DESC);
CREATE INDEX idx_teacher_daily_comments_student_date ON teacher_daily_comments(student_id, comment_date DESC);
CREATE INDEX idx_schedules_class_day_period ON schedules(class_id, day_of_week, period_no);
CREATE INDEX idx_menus_menu_date ON menus(menu_date);
CREATE INDEX idx_school_announcements_published_at ON school_announcements(published_at DESC);
CREATE INDEX idx_fee_records_student_status_due ON fee_records(student_id, status, due_date);
CREATE INDEX idx_chat_sessions_parent_started_at ON chat_sessions(parent_id, started_at DESC);
CREATE INDEX idx_chat_messages_session_created_at ON chat_messages(session_id, created_at);
CREATE INDEX idx_ai_audit_logs_session_created_at ON ai_audit_logs(session_id, created_at DESC);
CREATE INDEX idx_correction_logs_session_created_at ON correction_logs(session_id, created_at DESC);
CREATE INDEX idx_support_tickets_parent_status ON support_tickets(parent_id, status, created_at DESC);
CREATE INDEX idx_parent_notifications_parent_delivered_at ON parent_notifications(parent_id, delivered_at DESC);

-- Documentation comments
COMMENT ON TABLE parents IS 'Parent login accounts for the MVP.';
COMMENT ON TABLE parent_student_links IS 'Authorization mapping: chatbot must only access students linked to the logged-in parent.';
COMMENT ON TABLE teacher_daily_comments IS 'Teacher-written daily comments used as source material for respectful AI summaries.';
COMMENT ON TABLE ai_audit_logs IS 'Audit trail of each AI answer, including source metadata and freshness.';
COMMENT ON TABLE correction_logs IS 'Stores explicit user corrections such as "Thong tin nay sai".';
COMMENT ON TABLE support_tickets IS 'Escalation records when the parent wants to contact a teacher or support staff.';

COMMIT;
