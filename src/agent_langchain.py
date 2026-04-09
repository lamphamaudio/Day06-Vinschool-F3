import json
import os
import re
import unicodedata
from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from tools import (
    tools,
    get_student_schedule,
    get_student_grades,
    get_attendance_records,
    get_school_announcements,
    get_tuition_status,
    get_academic_summary,
    get_teacher_contact_info,
)
import database

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "system_prompt.md")


@lru_cache(maxsize=1)
def load_system_prompt():
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as file:
            return file.read().strip()
    return "Bạn là School Parent Assistant."


def _serialize_trace_value(value, max_chars=1600):
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
        except TypeError:
            text = str(value)

    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "\n..."
    return text


class StreamlitTraceHandler(BaseCallbackHandler):
    def __init__(self, trace_callback=None):
        self.trace_callback = trace_callback
        self.trace_steps = []
        self.tool_calls = []
        self.started = False

    def _publish(self, live=True):
        if self.trace_callback is not None:
            self.trace_callback(self.trace_steps, self.tool_calls, live)

    def _add_step(self, kind, title, detail):
        self.trace_steps.append({
            "kind": kind,
            "title": title,
            "detail": detail,
        })
        self._publish(live=True)

    def on_chain_start(self, serialized, inputs, **kwargs):
        if not self.started:
            self.started = True
            self._add_step(
                "thinking",
                "Tiếp nhận yêu cầu",
                "Đang phân tích câu hỏi và xác định dữ liệu cần tra cứu."
            )

    def on_agent_action(self, action, **kwargs):
        tool_name = getattr(action, "tool", "tool")
        self._add_step(
            "decision",
            "Chọn công cụ",
            f"Chuẩn bị gọi `{tool_name}` để lấy đúng dữ liệu trong hệ thống."
        )

    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "tool")
        self.tool_calls.append({
            "tool": tool_name,
            "input": _serialize_trace_value(input_str),
            "output": "",
            "status": "running",
        })
        self._add_step(
            "tool",
            "Đang gọi công cụ",
            f"`{tool_name}` đang được thực thi."
        )

    def on_tool_end(self, output, **kwargs):
        tool_name = "tool"
        if self.tool_calls:
            self.tool_calls[-1]["status"] = "completed"
            self.tool_calls[-1]["output"] = _serialize_trace_value(output)
            tool_name = self.tool_calls[-1]["tool"]

        self._add_step(
            "observation",
            "Đã nhận dữ liệu",
            f"`{tool_name}` đã trả về kết quả, đang tổng hợp phản hồi."
        )

    def on_agent_finish(self, finish, **kwargs):
        self._add_step(
            "answer",
            "Soạn câu trả lời",
            "Đang tổng hợp câu trả lời cuối cùng cho phụ huynh."
        )


def _normalize_text(value):
    if not value:
        return ""
    normalized = unicodedata.normalize("NFD", str(value).lower())
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    normalized = normalized.replace("đ", "d")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _needs_recheck_flow(query):
    normalized_query = _normalize_text(query)
    recheck_keywords = [
        "sai",
        "khong dung",
        "chua ro",
        "khong ro",
        "kiem tra lai",
        "check lai",
        "xem lai",
        "tra loi nay",
        "tra loi sai",
        "co ve sai",
        "chua chinh xac",
        "khong chinh xac",
        "toi khong hieu",
        "toi chua hieu",
        "giai thich lai",
    ]
    return any(keyword in normalized_query for keyword in recheck_keywords)


def _build_follow_up_guidance(query):
    if not _needs_recheck_flow(query):
        return (
            "Nếu câu hỏi bình thường, hãy chọn tool phù hợp nhất để trả lời. "
            "Chỉ dùng thông tin giáo viên chủ nhiệm khi phụ huynh thực sự cần liên hệ."
        )

    return (
        "Phụ huynh đang cho biết câu trả lời trước đó sai hoặc chưa rõ. "
        "BẮT BUỘC thực hiện đúng quy trình sau:\n"
        "1. Xin lỗi ngắn gọn và nói sẽ kiểm tra lại dữ liệu.\n"
        "2. Gọi lại tool dữ liệu phù hợp với chủ đề đang bị phản hồi để kiểm tra lại một lần nữa "
        "(ví dụ: lịch học -> get_student_schedule, điểm số -> get_student_grades, chuyên cần -> get_attendance_records, "
        "thông báo -> get_school_announcements, học phí -> get_tuition_status, nhận xét -> get_academic_summary hoặc get_teacher_comments).\n"
        "3. Sau khi kiểm tra lại, BẮT BUỘC gọi `get_teacher_contact_info` với `class_id` đã xác thực trong phiên.\n"
        "4. Nếu dữ liệu sau khi kiểm tra lại vẫn có khả năng sai, còn thiếu rõ ràng, hoặc phụ huynh vẫn đang nghi ngờ, "
        "hãy đưa thông tin liên hệ của giáo viên chủ nhiệm và khuyên phụ huynh liên hệ trực tiếp với giáo viên chủ nhiệm để xác minh.\n"
        "5. Chỉ gọi `report_issue_to_teacher` nếu phụ huynh muốn nhà trường/giáo viên tiếp nhận phản ánh hoặc nhờ hỗ trợ tiếp."
    )


def _add_manual_trace_step(trace_steps, tool_calls, trace_callback, kind, title, detail, live=True):
    trace_steps.append({
        "kind": kind,
        "title": title,
        "detail": detail,
    })
    if trace_callback is not None:
        trace_callback(trace_steps, tool_calls, live)


def _extract_previous_context(messages):
    last_user_message = ""
    last_assistant_message = ""

    for msg in reversed(messages):
        if not last_user_message and msg.get("role") == "user":
            last_user_message = msg.get("content", "")
            continue
        if not last_assistant_message and msg.get("role") == "assistant":
            last_assistant_message = msg.get("content", "")
        if last_user_message and last_assistant_message:
            break

    return last_user_message, last_assistant_message


def _extract_day_of_week(text):
    normalized_text = _normalize_text(text)
    for day in ["thu 2", "thu 3", "thu 4", "thu 5", "thu 6", "thu 7", "chu nhat"]:
        if day in normalized_text:
            if day == "chu nhat":
                return "Chủ Nhật"
            return "Thứ " + day.split(" ")[1]
    return None


def _infer_recheck_tool(context_text):
    normalized_text = _normalize_text(context_text)

    if any(keyword in normalized_text for keyword in ["hoc phi", "dong tien", "thanh toan", "phi"]):
        return "get_tuition_status"
    if any(keyword in normalized_text for keyword in ["diem danh", "vang", "vang mat", "di muon", "chuyen can", "attendance"]):
        return "get_attendance_records"
    if any(keyword in normalized_text for keyword in ["diem", "bai kiem tra", "ket qua", "giua ky", "cuoi ky", "quiz"]):
        return "get_student_grades"
    if any(keyword in normalized_text for keyword in ["thong bao", "su kien", "lich thi", "hop phu huynh", "meeting", "event"]):
        return "get_school_announcements"
    if any(keyword in normalized_text for keyword in ["thoi khoa bieu", "lich hoc", "mon gi", "tiet hoc", "hoc mon"]):
        return "get_student_schedule"
    return "get_academic_summary"


def _invoke_tool_with_trace(tool_obj, tool_name, tool_args, trace_steps, tool_calls, trace_callback):
    _add_manual_trace_step(
        trace_steps,
        tool_calls,
        trace_callback,
        "decision",
        "Chọn công cụ",
        f"Chuẩn bị gọi `{tool_name}` để kiểm tra lại dữ liệu."
    )

    tool_calls.append({
        "tool": tool_name,
        "input": _serialize_trace_value(tool_args),
        "output": "",
        "status": "running",
    })
    if trace_callback is not None:
        trace_callback(trace_steps, tool_calls, True)

    result = tool_obj.invoke(tool_args)
    tool_calls[-1]["status"] = "completed"
    tool_calls[-1]["output"] = _serialize_trace_value(result)

    _add_manual_trace_step(
        trace_steps,
        tool_calls,
        trace_callback,
        "observation",
        "Đã nhận dữ liệu",
        f"`{tool_name}` đã trả về kết quả để đối chiếu lại."
    )
    return result


def _format_schedule_recheck(schedule_rows):
    if not schedule_rows:
        return "Hiện em chưa thấy dữ liệu lịch học phù hợp trong hệ thống để đối chiếu lại."

    lines = []
    for row in schedule_rows[:5]:
        room = f", phòng {row.get('room_name')}" if row.get("room_name") else ""
        lines.append(
            f"- {row.get('day_of_week_text', 'Lịch học')}, tiết {row.get('period')} ({row.get('time_range', 'Chưa có khung giờ')}): "
            f"{row.get('subject')} với {row.get('teacher_name')}{room}"
        )
    return "Em đã kiểm tra lại lịch trong hệ thống:\n" + "\n".join(lines)


def _format_announcement_recheck(announcements):
    if not announcements:
        return "Hiện em chưa thấy thông báo hoặc sự kiện phù hợp trong hệ thống để đối chiếu lại."

    lines = []
    for ann in announcements[:3]:
        effective = ""
        if ann.get("effective_from") or ann.get("effective_to"):
            start = ann.get("effective_from") or "không rõ"
            end = ann.get("effective_to") or "không rõ"
            effective = f" | Hiệu lực: {start} đến {end}"
        lines.append(
            f"- {ann.get('title')} | Đăng lúc: {ann.get('date')}{effective}"
        )
    return "Em đã kiểm tra lại thông báo/sự kiện trong hệ thống:\n" + "\n".join(lines)



def _format_tuition_recheck(fee_rows):
    if not fee_rows:
        return "Hiện em chưa thấy khoản học phí nào trong hệ thống để đối chiếu lại."

    lines = []
    for fee in fee_rows[:5]:
        lines.append(
            f"- {fee.get('fee_name')}: {fee.get('amount')} VND | Hạn nộp: {fee.get('due_date')} | Trạng thái: {fee.get('status')}"
        )
    return "Em đã kiểm tra lại thông tin học phí:\n" + "\n".join(lines)


def _format_summary_recheck(summary_data):
    grades = summary_data.get("grades", []) if isinstance(summary_data, dict) else []
    attendance = summary_data.get("attendance", []) if isinstance(summary_data, dict) else []
    comments = summary_data.get("comments", []) if isinstance(summary_data, dict) else []

    summary_lines = ["Em đã kiểm tra lại dữ liệu học tập tổng hợp trong hệ thống:"]
    if grades:
        latest_grade = grades[0]
        summary_lines.append(
            f"- Điểm gần nhất: {latest_grade.get('subject')} {latest_grade.get('score')} điểm, cập nhật {latest_grade.get('updated_at')}"
        )
    if attendance:
        latest_attendance = attendance[0]
        summary_lines.append(
            f"- Chuyên cần gần nhất: {latest_attendance.get('date')} ở trạng thái {latest_attendance.get('status')}"
        )
    if comments:
        latest_comment = comments[0]
        summary_lines.append(
            f"- Nhận xét giáo viên gần nhất: {latest_comment.get('teacher_name')}: {latest_comment.get('comment')}"
        )

    if len(summary_lines) == 1:
        summary_lines.append("- Hiện chưa có dữ liệu tổng hợp rõ ràng để đối chiếu thêm.")
    return "\n".join(summary_lines)


def _format_teacher_contact(contact_info):
    if not contact_info:
        return "Hiện em chưa lấy được thông tin liên hệ giáo viên chủ nhiệm trong hệ thống."

    contact_parts = [
        f"Tên: {contact_info.get('teacher_name', 'Chưa rõ')}",
        f"SĐT: {contact_info.get('phone') or 'Chưa có'}",
        f"Email: {contact_info.get('email') or 'Chưa có'}",
    ]
    if contact_info.get("department"):
        contact_parts.append(f"Bộ phận: {contact_info.get('department')}")
    return "Thông tin liên hệ giáo viên chủ nhiệm:\n- " + "\n- ".join(contact_parts)


def _run_deterministic_recheck_flow(query, session_state, student_id, class_id, parent_id, trace_callback):
    trace_steps = []
    tool_calls = []
    history_before_current = session_state.get("messages", [])[:-1]
    previous_user_message, previous_assistant_message = _extract_previous_context(history_before_current)
    context_text = " ".join(filter(None, [previous_user_message, previous_assistant_message]))
    recheck_tool_name = _infer_recheck_tool(context_text)

    _add_manual_trace_step(
        trace_steps,
        tool_calls,
        trace_callback,
        "thinking",
        "Tiếp nhận phản hồi",
        "Phụ huynh cho biết câu trả lời trước đó sai hoặc chưa rõ, hệ thống sẽ kiểm tra lại dữ liệu một lần nữa."
    )

    tool_map = {
        "get_student_schedule": (
            get_student_schedule,
            {"class_id": class_id, "day_of_week": _extract_day_of_week(context_text)},
            _format_schedule_recheck,
        ),
        "get_school_announcements": (
            get_school_announcements,
            {"class_id": class_id},
            _format_announcement_recheck,
        ),
        "get_student_grades": (
            get_student_grades,
            {"student_id": student_id},
            _format_grades_recheck,
        ),
        "get_attendance_records": (
            get_attendance_records,
            {"student_id": student_id},
            _format_attendance_recheck,
        ),
        "get_tuition_status": (
            get_tuition_status,
            {"student_id": student_id},
            _format_tuition_recheck,
        ),
        "get_academic_summary": (
            get_academic_summary,
            {"student_id": student_id},
            _format_summary_recheck,
        ),
    }

    recheck_tool, recheck_args, recheck_formatter = tool_map[recheck_tool_name]
    recheck_result = _invoke_tool_with_trace(
        recheck_tool,
        recheck_tool_name,
        recheck_args,
        trace_steps,
        tool_calls,
        trace_callback,
    )

    teacher_contact = _invoke_tool_with_trace(
        get_teacher_contact_info,
        "get_teacher_contact_info",
        {"class_id": class_id},
        trace_steps,
        tool_calls,
        trace_callback,
    )

    _add_manual_trace_step(
        trace_steps,
        tool_calls,
        trace_callback,
        "answer",
        "Soạn câu trả lời",
        "Đã kiểm tra lại dữ liệu và chuẩn bị thông tin liên hệ giáo viên chủ nhiệm để hỗ trợ xác minh thêm.",
        live=False,
    )

    final_answer = (
        "Xin lỗi anh/chị vì thông tin trước đó có thể chưa chính xác hoặc chưa đủ rõ.\n\n"
        f"{recheck_formatter(recheck_result)}\n\n"
        f"{_format_teacher_contact(teacher_contact)}\n\n"
        "Nếu anh/chị vẫn thấy thông tin chưa khớp sau khi em đã kiểm tra lại, "
        "anh/chị nên liên hệ trực tiếp với giáo viên chủ nhiệm để được xác minh và hỗ trợ chính xác hơn."
    )

    database.insert_conversation_log(
        session_id=str(id(session_state)),
        student_id=student_id,
        parent_id=parent_id,
        intent_detected="LANGCHAIN_RECHECK",
        user_message=query,
        ai_response=final_answer,
        data_sources=[recheck_tool_name, "get_teacher_contact_info"],
        data_timestamps=[],
        escalated=False
    )

    return {
        "output": final_answer,
        "trace_steps": trace_steps,
        "tool_calls": tool_calls
    }

def get_langchain_agent_executor(api_key):
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """{base_system_prompt}

Dưới đây là thông tin bảo mật về con của phụ huynh đang chat với bạn.
LƯU Ý QUAN TRỌNG: nếu phụ huynh nhắc đến "con tôi", "cháu" hoặc không ghi rõ tên, hãy hiểu là đang hỏi về học sinh này.

- Tên học sinh: {student_name}
- Lớp: {class_name}
- Student ID: {student_id}
- Class ID: {class_id}
- Parent ID: {parent_id}

Ràng buộc cho flow hiện tại:
1. Tự động dùng các ID ở trên để gọi tool, không hỏi lại các ID này.
2. Chỉ trả lời trong phạm vi học sinh gắn với phiên đăng nhập hiện tại.
3. Nếu phụ huynh cố tình hỏi sang một học sinh khác, phải từ chối lịch sự để bảo vệ dữ liệu.
4. Có thể gọi liên tiếp nhiều tool nếu cần, nhưng chỉ kết luận những gì có trong dữ liệu.
5. Với lịch học, thông báo, sự kiện hoặc mốc thời gian học tập, phải nêu rõ thời gian nếu tool có cung cấp.
6. Với học phí, đặt lịch, phản ánh hoặc hỗ trợ, chỉ hướng dẫn và xác nhận bước tiếp theo; không được giả định giao dịch cuối cùng đã hoàn tất nếu dữ liệu chưa xác nhận.

Chỉ dẫn theo ngữ cảnh:
{follow_up_guidance}
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

def call_langchain_agent(api_key, query, session_state, trace_callback=None):
    student_data = session_state.get("student_data", {}).get("student", {})
    parent_info = session_state.get("parent_info", {})
    
    student_id = student_data.get("student_id")
    class_id = student_data.get("class_id")
    class_name = student_data.get("class_name")
    student_name = student_data.get("full_name")
    parent_id = parent_info.get("parent_id")
    follow_up_guidance = _build_follow_up_guidance(query)
    base_system_prompt = load_system_prompt()

    if not student_id or not parent_id:
        return {
            "output": "Vui lòng đăng nhập lại.",
            "trace_steps": [],
            "tool_calls": []
        }

    if _needs_recheck_flow(query):
        return _run_deterministic_recheck_flow(
            query=query,
            session_state=session_state,
            student_id=student_id,
            class_id=class_id,
            parent_id=parent_id,
            trace_callback=trace_callback,
        )

    # Khởi tạo hoặc lấy lịch sử chat từ session_state
    chat_history = []
    for msg in session_state.get("messages", [])[-5:]: # Lấy 5 tin nhắn gần nhất
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        else:
            chat_history.append(AIMessage(content=msg["content"]))

    executor = get_langchain_agent_executor(api_key)
    trace_handler = StreamlitTraceHandler(trace_callback=trace_callback)
    
    try:
        response = executor.invoke({
            "input": query,
            "chat_history": chat_history,
            "student_id": student_id,
            "class_id": class_id,
            "parent_id": parent_id,
            "student_name": student_name,
            "class_name": class_name,
            "base_system_prompt": base_system_prompt,
            "follow_up_guidance": follow_up_guidance
        }, config={"callbacks": [trace_handler]})
        
        final_answer = response["output"]
        trace_handler._publish(live=False)
        
        # Log vào database (sử dụng hàm cũ từ database.py)
        database.insert_conversation_log(
            session_id=str(id(session_state)),
            student_id=student_id,
            parent_id=parent_id,
            intent_detected="LANGCHAIN_AGENT",
            user_message=query,
            ai_response=final_answer,
            data_sources=["langchain_tools"],
            data_timestamps=[],
            escalated=False
        )
        
        return {
            "output": final_answer,
            "trace_steps": trace_handler.trace_steps,
            "tool_calls": trace_handler.tool_calls
        }
    except Exception as e:
        print(f"LangChain Error: {e}")
        return {
            "output": f"Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}",
            "trace_steps": trace_handler.trace_steps,
            "tool_calls": trace_handler.tool_calls
        }
