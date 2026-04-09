from langchain_core.tools import tool
import database

# ĐỊNH NGHĨA TOOLS THEO CHUẨN LANGCHAIN
# Các hàm này sẽ được Agent tự động gọi dựa trên câu hỏi của người dùng

@tool
def get_student_schedule(class_id: str, day_of_week: str = None):
    """Tra cứu thời khóa biểu của lớp học. day_of_week có thể là 'Thứ 2' đến 'Thứ 7'."""
    return database.get_schedule(class_id, day_of_week)

@tool
def get_student_grades(student_id: str):
    """Tra cứu bảng điểm và kết quả học tập của học sinh."""
    return database.get_grades(student_id)

@tool
def get_attendance_records(student_id: str):
    """Tra cứu lịch sử điểm danh và sự chuyên cần của học sinh."""
    return database.get_attendance(student_id)

@tool
def get_school_announcements(class_id: str = None):
    """Lấy các thông báo mới từ nhà trường và giáo viên."""
    return database.get_announcements(class_id)

@tool
def get_tuition_status(student_id: str):
    """Kiểm tra tình trạng đóng học phí và các khoản phí khác."""
    return database.get_tuition(student_id)

@tool
def get_academic_summary(student_id: str):
    """Lấy bản tổng hợp nhận xét của giáo viên và tình hình học tập chung."""
    return database.get_summary_context(student_id)

@tool
def report_issue_to_teacher(parent_id: str, student_id: str, issue_description: str, category: str = "general_support"):
    """Gửi phản hồi, khiếu nại hoặc yêu cầu hỗ trợ tới giáo viên/nhà trường. 
    Category có thể là: 'wrong_information', 'academic_concern', 'fee_issue', 'general_support'."""
    return database.create_support_ticket(student_id, parent_id, issue_description, category)

# Danh sách tools để export
tools = [
    get_student_schedule,
    get_student_grades,
    get_attendance_records,
    get_school_announcements,
    get_tuition_status,
    get_academic_summary,
    report_issue_to_teacher
]
