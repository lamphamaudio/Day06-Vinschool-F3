import os
import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta
from database import (
    get_schedule,
    get_grades,
    get_attendance,
    get_announcements,
    get_summary_context,
    get_tuition,
    create_support_ticket,
    insert_conversation_log
)

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')

def load_system_prompt():
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return "Bạn là trợ lý AI."

def check_stale(timestamp_str, hours_limit):
    try:
        updated = datetime.fromisoformat(timestamp_str)
        if datetime.now() - updated > timedelta(hours=hours_limit):
            return True
        return False
    except:
        return False

@st.cache_data(ttl=3600)
def classify_intent_cached(api_key, query):
    client = OpenAI(api_key=api_key)
    intent_prompt = """
    Bạn là bộ phận phân loại câu hỏi (Router). Hãy trả về đúng 1 từ khóa (INTENT) thuộc danh sách sau, không giải thích:
    - SCHEDULE: lịch học, thời khóa biểu
    - GRADES: điểm, kết quả học tập, bài kiểm tra
    - ATTENDANCE: điểm danh, có mặt, vắng mặt
    - NOTIFICATION: thông báo, sự kiện, lịch thi
    - STUDENT_SUMMARY: tình hình học tập, con học thế nào
    - TUITION: học phí, đóng tiền
    - APPOINTMENT: gặp giáo viên
    - ESCALATION: thông tin sai, phàn nàn
    - OUT_OF_SCOPE: không rõ ràng
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": intent_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0,
            timeout=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Intent Error: {e}")
        return "ERROR"

def extract_db_context_and_direct_format(intent, student_id, class_name, student_name):
    """
    Kéo data và Nếu thuộc nhóm Câu hỏi đơn giản: SQL trực tiếp tạo response KHÔNG CẦN gọi LLM
    """
    context_lines = []
    data_sources = []
    data_timestamps = []
    
    # Định dạng Header chuẩn bắt buộc
    dt_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    common_header = f"---\n👤 Học sinh: {student_name} | Lớp: {class_name}\n📅 Dữ liệu truy xuất gốc theo DB: {dt_now}\n---\n"
    common_footer = "\n\n[ Thông tin này sai ] [ Liên hệ giáo viên ]"

    direct_response = None
    
    if intent == "SCHEDULE":
        schedule = get_schedule(class_name)
        for s in schedule:
            context_lines.append(f"- Tiết {s['period']} | Môn: {s['subject']} | GV: {s['teacher_name']}")
        data_sources.append("schedule")
        direct_response = common_header + "📚 **Lịch học**:\n" + "\n".join(context_lines) + common_footer
            
    elif intent == "GRADES":
        grades = get_grades(student_id)
        for g in grades:
            stale = check_stale(g['updated_at'], 24)
            warn = " *(CẢNH BÁO: Dữ liệu chưa đồng bộ >24h)*" if stale else ""
            context_lines.append(f"- **Môn {g['subject']}**: {g['score']} điểm ({g['type']}) | Cập nhật: {g['updated_at']}{warn}")
            data_timestamps.append(g['updated_at'])
        data_sources.append("grades")
        # Direct SQL answer bypass LLM
        direct_response = common_header + "📊 **Điểm số cập nhật**:\n" + "\n".join(context_lines) + common_footer
            
    elif intent == "ATTENDANCE":
        attendance = get_attendance(student_id)
        for a in attendance:
            stale = check_stale(a['updated_at'], 1)
            warn = " *(CẢNH BÁO: Dữ liệu bị delay >1h)*" if stale else ""
            context_lines.append(f"- Ngày {a['date']}: **{a['status']}** | Cập nhật: {a['updated_at']}{warn}")
            data_timestamps.append(a['updated_at'])
        data_sources.append("attendance")
        direct_response = common_header + "✋ **Tình trạng chuyên cần**:\n" + "\n".join(context_lines) + common_footer

    elif intent == "TUITION":
        tuition = get_tuition(student_id)
        for t in tuition:
            context_lines.append(f"- Khoản phí: **{t['fee_name']}** | Số tiền: {t['amount']} VNĐ | Hạn nộp: {t['due_date']} | Trạng thái: **{t['status']}**")
        data_sources.append("tuition")
        direct_response = common_header + "💳 **Tình trạng học phí**:\n" + "\n".join(context_lines) + "\n\n_Vui lòng thanh toán qua cổng nhà trường theo đường dẫn gửi kèm Email._" + common_footer
            
    elif intent == "NOTIFICATION":
        announcements = get_announcements(class_name)
        for ann in announcements:
            stale = check_stale(ann['date'], 1)
            warn = " *(CẢNH BÁO: Notification delay >1h)*" if stale else ""
            context_lines.append(f"- **{ann['title']}** (Ngày {ann['date']}): {ann['content']} {warn}\n  🔗 Link: {ann['link']}")
            data_timestamps.append(ann['date'])
        data_sources.append("announcements")
        direct_response = common_header + "📢 **Thông báo mới nhất**:\n" + "\n".join(context_lines) + common_footer
            
    elif intent == "STUDENT_SUMMARY":
        summary = get_summary_context(student_id)
        context_lines.append("--- DB TỔNG HỢP ---")
        context_lines.append(str(summary))
        data_sources.extend(["grades", "attendance", "comments"])

    return "\n".join(context_lines), data_sources, data_timestamps, direct_response

def call_ai_agent(api_key, query, session_state):
    """
    Xử lý: Session Binding + Graceful Degradation + Cost limit bypassing LLM + Streaming ready
    """
    student_data_meta = session_state.get("student_data", {})
    parent_info = session_state.get("parent_info", {})
    
    student = student_data_meta.get("student", {})
    student_id = student.get("student_id")
    class_name = student.get("class_name")
    student_name = student.get("full_name", "N/A")
    parent_id = parent_info.get("parent_id")
    
    # 1. SESSION BINDING CHECK
    if not student_id or not parent_id:
        return "Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại."

    try:
        # 2. INTENT CLASSIFICATION
        intent = classify_intent_cached(api_key, query)
        
        if intent == "ERROR":
            raise Exception("Intent classification failed or timed out.")
            
        # 3. EXTRACTION AND BYPASS EVALUATION
        db_context, data_sources, data_timestamps, direct_response = extract_db_context_and_direct_format(intent, student_id, class_name, student_name)
        
        # 4. LLM GENERATION OR DIRECT RETURN (CHỐNG LÃNG PHÍ INFERENCE COST THEO YÊU CẦU DEPLOYMENT)
        if direct_response and intent in ["SCHEDULE", "GRADES", "ATTENDANCE", "TUITION", "NOTIFICATION"]:
            final_answer = direct_response
        else:
            client = OpenAI(api_key=api_key)
            system_prompt = load_system_prompt()
            max_tokens = 1000 if intent == "STUDENT_SUMMARY" else 600

            full_system_instruction = f"""{system_prompt}

=== THÔNG TIN HỌC SINH HIỆN TẠI GẮN VỚI TÀI KHOẢN (DO NOT REASON ABOUT OTHER STUDENTS) ===
Học sinh: {student_name} - Lớp: {class_name}

=== DỮ LIỆU ĐƯỢC QUERY (Intent phân loại: {intent}) ===
{db_context}
===================================
Bạn phải trả lời theo nguyên tắc "FORMAT TRẢ LỜI CHUẨN" có Header và CẤU TRÚC NHẬN XÉT HỌC SINH tích cực trong System Prompt.
"""
            messages = [{"role": "system", "content": full_system_instruction}]
            chat_history = session_state.get("messages", [])[:-1]
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": query})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2, 
                max_tokens=max_tokens,
                timeout=25 # Streamlit free có hard timeout ~30s
            )
            final_answer = response.choices[0].message.content
        
        # 5. LOGGING
        session_id = str(id(session_state))
        insert_conversation_log(
            session_id=session_id,
            student_id=student_id,
            parent_id=parent_id,
            intent_detected=intent,
            user_message=query,
            ai_response=final_answer,
            data_sources=data_sources,
            data_timestamps=data_timestamps,
            escalated=(intent == "ESCALATION"),
            correction_flagged=False
        )
        return final_answer
        
    except psycopg2.errors.OperationalError as db_e:
         raise db_e # Truyền lên UI xử lý cảnh báo Cold Start
    except Exception as e:
        print(f"Graceful Degradation Triggered: {e}")
        return "Hệ thống dữ liệu đang tạm gián đoạn. Vui lòng thử lại sau hoặc liên hệ giáo viên nếu cần xử lý gấp."
