import database
from datetime import datetime

# ĐỊNH NGHĨA CÁC TOOLS CHO AI AGENT
# File này chứa logic xử lý nghiệp vụ trung gian giữa Agent và Database

def tool_get_student_schedule(class_id, day_of_week=None):
    """Lấy thời khóa biểu của lớp học."""
    return database.get_schedule(class_id, day_of_week)

def tool_get_student_grades(student_id):
    """Lấy bảng điểm của học sinh."""
    return database.get_grades(student_id)

def tool_get_attendance_records(student_id):
    """Lấy danh sách điểm danh của học sinh."""
    return database.get_attendance(student_id)

def tool_get_school_announcements(class_id=None):
    """Lấy các thông báo mới nhất từ nhà trường."""
    return database.get_announcements(class_id)

def tool_get_tuition_status(student_id):
    """Tra cứu tình trạng học phí."""
    return database.get_tuition(student_id)

def tool_get_academic_summary(student_id):
    """Tổng hợp tình hình học tập (Điểm, chuyên cần, nhận xét)."""
    return database.get_summary_context(student_id)

def tool_report_issue_to_teacher(student_id, parent_id, issue_description, category="general_support"):
    """Tạo ticket gửi yêu cầu hỗ trợ hoặc báo cáo lỗi thông tin cho giáo viên."""
    return database.create_support_ticket(student_id, parent_id, issue_description, category)

# MẪU ĐỊNH NGHĨA JSON CHO OPENAI TOOL CALLING (Nếu bạn muốn nâng cấp sau này)
AVAILABLE_TOOLS_METADATA = [
    {
        "type": "function",
        "function": {
            "name": "tool_get_student_schedule",
            "description": "Tra cứu lịch học/thời khóa biểu của học sinh.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day_of_week": {"type": "string", "description": "Thứ trong tuần (Thứ 2 - Thứ 7)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_report_issue_to_teacher",
            "description": "Báo cáo thông tin sai hoặc gửi khiếu nại tới giáo viên.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_description": {"type": "string", "description": "Nội dung phản hồi"},
                    "category": {"type": "string", "enum": ["wrong_information", "academic_concern", "fee_issue"]}
                },
                "required": ["issue_description"]
            }
        }
    }
]
