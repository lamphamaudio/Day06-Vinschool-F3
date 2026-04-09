import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor
import psycopg2.pool
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_db_pool():
    try:
        db_url = st.secrets["DATABASE_URL"]
    except:
        db_url = os.getenv("DATABASE_URL")
        
    if not db_url:
        raise ValueError("DATABASE_URL khÃ´ng Ä‘Æ°á»£c tÃ¬m tháº¥y")
        
    # Táº¡o pool tá»‘i Æ°u connection timeout
    # Set search_path to school_ai for all connections in the pool
    return psycopg2.pool.SimpleConnectionPool(1, 10, db_url, connect_timeout=5, options='-c search_path=school_ai,public -c statement_timeout=8000')

def get_connection():
    pool = get_db_pool()
    return pool.getconn()

def return_connection(conn):
    pool = get_db_pool()
    pool.putconn(conn)

def _execute_query(query, params, fetch_one=False, commit=False):
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(query, params)
        if commit:
            conn.commit()
            if cursor.description:
                result = cursor.fetchone() if fetch_one else cursor.fetchall()
            else:
                result = None
        else:
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        if commit: conn.rollback()
        raise e
    finally:
         return_connection(conn)

# CÃC HÃ€M GET Dá»® LIá»†U ÄÃƒ Cáº¬P NHáº¬T THEO SCHEMA school_ai
def authenticate_parent(login_identifier, password):
    # TÃ¬m parent theo email hoáº·c parent_code (thay cho username)
    query = "SELECT id, full_name FROM parents WHERE (email = %s OR parent_code = %s) AND password_hash = %s"
    parent = _execute_query(query, (login_identifier, login_identifier, password), fetch_one=True)
    
    if parent:
        # Láº¥y student_id Ä‘áº§u tiÃªn (máº·c Ä‘á»‹nh) liÃªn káº¿t vá»›i parent nÃ y
        mapping = _execute_query("SELECT student_id FROM parent_student_links WHERE parent_id = %s LIMIT 1", (parent['id'],), fetch_one=True)
        if mapping:
            return {"parent_id": str(parent['id']), "parent_name": parent['full_name'], "student_id": str(mapping['student_id'])}
    return None

def get_student_info(student_id):
    query = """
    SELECT s.id as student_id, s.full_name, s.student_code, c.class_name, c.id as class_id
    FROM students s
    JOIN classes c ON s.class_id = c.id
    WHERE s.id = %s
    """
    student = _execute_query(query, (student_id,), fetch_one=True)
    return dict(student) if student else {}

def get_schedule(class_id, day_of_week=None):
    # day_of_week mapping from Vietnamese string to SMALLINT (1-7)
    day_map = {'Thá»© 2': 1, 'Thá»© 3': 2, 'Thá»© 4': 3, 'Thá»© 5': 4, 'Thá»© 6': 5, 'Thá»© 7': 6, 'Chá»§ Nháº­t': 7}
    if not day_of_week: 
        day_val = 4 # Mock Thá»© 5
    else:
        day_val = day_map.get(day_of_week, 4)

    query = """
    SELECT s.period_no as period, sub.subject_name as subject, t.full_name as teacher_name
    FROM schedules s
    JOIN subjects sub ON s.subject_id = sub.id
    JOIN teachers t ON s.teacher_id = t.id
    WHERE s.class_id = %s AND s.day_of_week = %s
    ORDER BY s.period_no
    """
    rows = _execute_query(query, (class_id, day_val))
    return [dict(row) for row in rows]

def get_grades(student_id):
    query = """
    SELECT sub.subject_name as subject, g.score, g.assessment_name as type, g.recorded_at as updated_at
    FROM grade_records g
    JOIN subjects sub ON g.subject_id = sub.id
    WHERE g.student_id = %s
    ORDER BY g.recorded_at DESC
    """
    rows = _execute_query(query, (student_id,))
    result = []
    for row in rows:
        d = dict(row)
        d['updated_at'] = d['updated_at'].isoformat()
        result.append(d)
    return result

def get_attendance(student_id):
    query = """
    SELECT attendance_date as date, status, created_at as updated_at
    FROM attendance_records
    WHERE student_id = %s
    ORDER BY attendance_date DESC
    """
    rows = _execute_query(query, (student_id,))
    # Format date to string to match agent.py expectation if needed
    result = []
    for row in rows:
        d = dict(row)
        d['date'] = d['date'].strftime("%Y-%m-%d")
        d['updated_at'] = d['updated_at'].isoformat()
        result.append(d)
    return result

def get_announcements(class_id=None):
    if class_id:
        query = """
        SELECT DISTINCT
            sa.id,
            sa.title,
            sa.content,
            sa.category,
            sa.audience_scope,
            sa.published_at AS date,
            sa.effective_from,
            sa.effective_to
        FROM school_announcements sa
        LEFT JOIN announcement_targets at ON at.announcement_id = sa.id
        WHERE
            (
                sa.audience_scope = 'all'
                OR at.class_id = %s
            )
            AND (sa.effective_from IS NULL OR sa.effective_from <= NOW())
            AND (sa.effective_to IS NULL OR sa.effective_to >= NOW())
        ORDER BY sa.published_at DESC
        LIMIT 5
        """
        rows = _execute_query(query, (class_id,))
    else:
        query = """
        SELECT
            sa.id,
            sa.title,
            sa.content,
            sa.category,
            sa.audience_scope,
            sa.published_at AS date,
            sa.effective_from,
            sa.effective_to
        FROM school_announcements sa
        WHERE
            sa.audience_scope = 'all'
            AND (sa.effective_from IS NULL OR sa.effective_from <= NOW())
            AND (sa.effective_to IS NULL OR sa.effective_to >= NOW())
        ORDER BY sa.published_at DESC
        LIMIT 5
        """
        rows = _execute_query(query, ())

    result = []
    for row in rows:
        d = dict(row)
        d["id"] = str(d["id"])
        d["date"] = d["date"].isoformat() if d["date"] else None
        d["effective_from"] = d["effective_from"].isoformat() if d["effective_from"] else None
        d["effective_to"] = d["effective_to"].isoformat() if d["effective_to"] else None
        result.append(d)
    return result
def get_parent_notifications(student_id):
    query = """
    SELECT
        id,
        parent_id,
        student_id,
        announcement_id,
        title,
        content,
        category,
        is_read,
        delivered_at,
        read_at
    FROM parent_notifications
    WHERE student_id = %s
    ORDER BY delivered_at DESC
    LIMIT 10
    """
    rows = _execute_query(query, (student_id,))
    result = []
    for row in rows:
        d = dict(row)
        d["id"] = str(d["id"])
        d["parent_id"] = str(d["parent_id"]) if d.get("parent_id") else None
        d["student_id"] = str(d["student_id"]) if d.get("student_id") else None
        d["announcement_id"] = str(d["announcement_id"]) if d.get("announcement_id") else None
        d["delivered_at"] = d["delivered_at"].isoformat() if d["delivered_at"] else None
        d["read_at"] = d["read_at"].isoformat() if d["read_at"] else None
        result.append(d)
    return result

def get_summary_context(student_id):
    grades = get_grades(student_id)
    attendance = get_attendance(student_id)
    # Láº¥y thÃªm comment cá»§a giÃ¡o viÃªn tá»« báº£ng teacher_daily_comments
    comments_rows = _execute_query("SELECT comment_text as comment, t.full_name as teacher_name FROM teacher_daily_comments c JOIN teachers t ON c.teacher_id = t.id WHERE student_id = %s", (student_id,))
    comments = [dict(row) for row in comments_rows]
    return {"grades": grades, "attendance": attendance, "comments": comments}

def get_tuition(student_id):
    query = "SELECT fee_name, amount, due_date, status FROM fee_records WHERE student_id = %s"
    rows = _execute_query(query, (student_id,))
    result = []
    for row in rows:
        d = dict(row)
        d['due_date'] = d['due_date'].strftime("%Y-%m-%d") if d['due_date'] else "N/A"
        result.append(d)
    return result

def create_support_ticket(student_id, parent_id, issue, category="general_support"):
    query = """
    INSERT INTO support_tickets (ticket_code, parent_id, student_id, category, title, description, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    ticket_code = f"TK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    title = f"Há»— trá»£: {issue[:30]}..."
    result = _execute_query(query, (ticket_code, parent_id, student_id, category, title, issue, "open"), fetch_one=True, commit=True)
    return result[0] if result else None

def insert_conversation_log(session_id, student_id, parent_id, intent_detected, user_message, ai_response, data_sources, data_timestamps, escalated=False, correction_flagged=False):
    import json
    import uuid
    
    # Chuáº©n hÃ³a session_id thÃ nh UUID
    try:
        uuid.UUID(str(session_id))
        final_session_id = str(session_id)
    except:
        final_session_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(session_id)))

    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Äáº£m báº£o session tá»“n táº¡i trong chat_sessions (vÃ¬ cÃ³ khÃ³a ngoáº¡i)
        cursor.execute("SELECT id FROM chat_sessions WHERE id = %s", (final_session_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO chat_sessions (id, parent_id, student_id) VALUES (%s, %s, %s)",
                (final_session_id, parent_id, student_id)
            )
            
        # 2. Log vÃ o ai_audit_logs
        query = """
        INSERT INTO ai_audit_logs (session_id, parent_id, student_id, question_text, answer_text, intent_name, data_sources, was_escalated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (final_session_id, parent_id, student_id, user_message, ai_response, intent_detected, json.dumps(data_sources), escalated))
        
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Log Error: {e}")
    finally:
        return_connection(conn)

