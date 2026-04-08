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
        raise ValueError("DATABASE_URL không được tìm thấy")
        
    # Tạo pool tối ưu connection timeout
    return psycopg2.pool.SimpleConnectionPool(1, 10, db_url, connect_timeout=5, options='-c statement_timeout=8000')

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
    except psycopg2.errors.OperationalError as e:
        if commit: conn.rollback()
        raise e
    except Exception as e:
        if commit: conn.rollback()
        raise e
    finally:
         return_connection(conn)

# CÁC HÀM GET DỮ LIỆU TÁCH RỜI / FETCH THEO INTENT KHÔNG TẢI TOÀN BỘ DATA
def authenticate_parent(username, password):
    parent = _execute_query("SELECT parent_id, full_name FROM parents WHERE username = %s AND password = %s", (username, password), fetch_one=True)
    student_id = None
    if parent:
        mapping = _execute_query("SELECT student_id FROM parent_student_mapping WHERE parent_id = %s", (parent['parent_id'],), fetch_one=True)
        if mapping:
            student_id = mapping['student_id']
    if student_id:
        return {"parent_id": parent['parent_id'], "parent_name": parent['full_name'], "student_id": student_id}
    return None

def get_student_info(student_id):
    student = _execute_query("SELECT * FROM students WHERE student_id = %s", (student_id,), fetch_one=True)
    return dict(student) if student else {}

def get_schedule(class_name, day_of_week=None):
    if not day_of_week: day_of_week = 'Thứ 5' # Mock
    rows = _execute_query("SELECT * FROM schedule WHERE class_name = %s AND day_of_week = %s ORDER BY period", (class_name, day_of_week))
    return [dict(row) for row in rows]

def get_grades(student_id):
    rows = _execute_query("SELECT * FROM grades WHERE student_id = %s ORDER BY updated_at DESC", (student_id,))
    return [dict(row) for row in rows]

def get_attendance(student_id):
    rows = _execute_query("SELECT * FROM attendance WHERE student_id = %s ORDER BY date DESC", (student_id,))
    return [dict(row) for row in rows]

def get_announcements(class_name):
    rows = _execute_query("SELECT * FROM announcements WHERE class_name = %s ORDER BY date DESC", (class_name,))
    return [dict(row) for row in rows]

def get_summary_context(student_id):
    grades = [dict(row) for row in _execute_query("SELECT subject, score, updated_at FROM grades WHERE student_id = %s", (student_id,))]
    attendance = [dict(row) for row in _execute_query("SELECT status, date FROM attendance WHERE student_id = %s LIMIT 10", (student_id,))]
    comments = [dict(row) for row in _execute_query("SELECT teacher_name, subject, comment FROM comments WHERE student_id = %s", (student_id,))]
    return {"grades": grades, "attendance": attendance, "comments": comments}

def get_tuition(student_id):
    rows = _execute_query("SELECT fee_name, amount, due_date, status FROM tuition WHERE student_id = %s", (student_id,))
    return [dict(row) for row in rows]

def create_support_ticket(student_id, issue, recipient):
    created_at = datetime.now().isoformat()
    # Dùng query thủ công cho returning
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO support_tickets (student_id, issue, recipient, status, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                        (student_id, issue, recipient, "Open", created_at))
        ticket_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        return ticket_id
    except:
        conn.rollback()
        raise
    finally:
        return_connection(conn)

def insert_conversation_log(session_id, student_id, parent_id, intent_detected, user_message, ai_response, data_sources, data_timestamps, escalated=False, correction_flagged=False):
    timestamp = datetime.now().isoformat()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversation_log (session_id, student_id, parent_id, timestamp, intent_detected, user_message, ai_response, data_sources, data_timestamps, escalated, correction_flagged) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (session_id, student_id, parent_id, timestamp, intent_detected, user_message, ai_response, str(data_sources), str(data_timestamps), escalated, correction_flagged)
        )
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Log Error: {e}")
    finally:
        return_connection(conn)
