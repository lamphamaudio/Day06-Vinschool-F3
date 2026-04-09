import streamlit as st
import psycopg2.errors
from database import authenticate_parent, get_student_info
from agent_langchain import call_langchain_agent
import time
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

st.set_page_config(page_title="Hỗ trợ Phụ huynh - VinSchool/VinUni", page_icon="🏫", layout="centered")

st.markdown("""
<style>
.chat-container { border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["parent_info"] = None
    st.session_state["student_data"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "api_key" not in st.session_state:
    # Lấy key từ secrets để tuân thủ bảo mật
    try:
        st.session_state["api_key"] = st.secrets["OPENAI_API_KEY"]
    except:
        st.session_state["api_key"] = os.getenv("OPENAI_API_KEY", "")

def login_page():
    st.title("🏫 Hệ thống Hỗ trợ Phụ huynh")
    st.markdown("Vui lòng đăng nhập để tra cứu thông tin học tập của con (Hỗ trợ 24/7).")
    
    with st.form("login_form"):
        username = st.text_input("Mã phụ huynh hoặc Email")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")
        
        if submitted:
            try:
                user_info = authenticate_parent(username, password)
                if user_info:
                    st.session_state["logged_in"] = True
                    st.session_state["parent_info"] = user_info
                    
                    # Fetch mock initial data needed for UI context
                    st.session_state["student_data"] = {"student": get_student_info(user_info["student_id"])}
                    st.session_state["messages"] = []
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")
            except psycopg2.errors.OperationalError:
                st.warning("Hệ thống Database đang khởi động lại (Cold Start) theo chế độ tự động tắt tiết kiệm điền của hệ thống, vui lòng chờ 10-15 giây...")
                st.button("Thử lại")
                st.stop()
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")
    
    st.info("💡 Mẹo: Dùng tài khoản mẫu `parentA@example.com` hoặc `PH001` / pass: `123456`")

def chat_page():
    parent_name = st.session_state["parent_info"]["parent_name"]
    student = st.session_state["student_data"].get("student", {})
    
    with st.sidebar:
        st.subheader("Cài đặt & Hồ sơ")
        st.markdown(f"**Phụ huynh:** {parent_name}")
        st.markdown(f"**Học sinh:** {student.get('full_name')} - Lớp: {student.get('class_name')}")
        st.divider()
        
        st.session_state["api_key"] = st.text_input("Mã API OpenAI", type="password", value=st.session_state.get("api_key", ""))
        
        if st.button("Đăng xuất"):
            st.session_state["logged_in"] = False
            for key in ["parent_info", "student_data", "messages"]:
                st.session_state[key] = None
            st.session_state["messages"] = []
            st.rerun()
            
    st.title("Hỏi đáp trực tuyến")
    st.caption("AI Assistant cung cấp thông tin học tập nhanh chóng.")

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Hỏi AI về khóa học, điểm số, hoặc nhận xét..."):
        if not st.session_state["api_key"]:
            st.error("Vui lòng nhập Mã API OpenAI trong menu Cài đặt (Bên trái) trước khi hỏi.")
            return
            
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Đang tra cứu cơ sở dữ liệu..."):
                try:
                    response = call_langchain_agent(
                        api_key=st.session_state["api_key"],
                        query=prompt,
                        session_state=st.session_state
                    )
                    
                    # Mô phỏng hiệu ứng stream text
                    full_response = ""
                    for chunk in response.split(" "):
                        full_response += chunk + " "
                        time.sleep(0.01)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                        
                except psycopg2.errors.OperationalError:
                     st.warning("Hệ thống Database đang khởi động lại (Cold Start), vui lòng chờ 10-15 giây...")
                     if st.button("Thử lại truy vấn"): st.rerun()
                     return
                
        st.session_state["messages"].append({"role": "assistant", "content": response})

if __name__ == "__main__":
    if st.session_state["logged_in"]:
        chat_page()
    else:
        login_page()
