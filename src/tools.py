from langchain_core.tools import tool

import database


def tool_get_student_schedule(class_id, day_of_week=None):
    """Lay thoi khoa bieu cua lop hoc."""
    return database.get_schedule(class_id, day_of_week)


def tool_get_student_grades(student_id):
    """Lay bang diem cua hoc sinh."""
    return database.get_grades(student_id)


def tool_get_attendance_records(student_id):
    """Lay danh sach diem danh cua hoc sinh."""
    return database.get_attendance(student_id)


@tool
def tool_get_school_announcements(class_id: str = "") -> str:
    """
    Lay cac thong bao moi nhat tu nha truong.
    Tham so:
    - class_id: ID lop hoc. Co the bo trong neu muon lay thong bao chung toan truong.
    Tra ve danh sach thong bao moi nhat phu hop voi lop hoac toan truong.
    """
    announcements = database.get_announcements(class_id or None)

    if not announcements:
        return "Khong co thong bao nao phu hop."

    lines = ["Thong bao nha truong moi nhat:"]
    lines.extend(
        f"{idx}. {item['title']} | Loai: {item.get('category', 'general')} | "
        f"Ngay dang: {item['date']} | Noi dung: {item['content']}"
        for idx, item in enumerate(announcements, 1)
    )
    return "\n".join(lines)


@tool
def tool_get_parent_notifications(student_id: str) -> str:
    """
    Lay thong bao danh cho phu huynh.
    Tham so:
    - student_id: ID hoc sinh can lay thong bao da gui cho phu huynh.
    Tra ve cac thong bao moi nhat ma phu huynh can theo doi.
    """
    notifications = database.get_parent_notifications(student_id)

    if not notifications:
        return "Hien tai khong co thong bao nao danh cho phu huynh."

    lines = ["Thong bao gui cho phu huynh:"]
    lines.extend(
        f"{idx}. {item['title']} | Loai: {item.get('category', 'general')} | "
        f"Thoi gian gui: {item['delivered_at']} | "
        f"Trang thai: {'Da doc' if item['is_read'] else 'Chua doc'} | "
        f"Noi dung: {item['content']}"
        for idx, item in enumerate(notifications, 1)
    )
    return "\n".join(lines)


def tool_get_tuition_status(student_id):
    """Tra cuu tinh trang hoc phi."""
    return database.get_tuition(student_id)


def tool_get_academic_summary(student_id):
    """Tong hop tinh hinh hoc tap (Diem, chuyen can, nhan xet)."""
    return database.get_summary_context(student_id)


def tool_report_issue_to_teacher(
    student_id, parent_id, issue_description, category="general_support"
):
    """Tao ticket gui yeu cau ho tro hoac bao cao loi thong tin cho giao vien."""
    return database.create_support_ticket(
        student_id, parent_id, issue_description, category
    )


def tool_get_teacher_contact_info(teacher_id):
    """Lay thong tin lien he cua giao vien."""
    return database.get_teacher_contact(teacher_id)


AVAILABLE_TOOLS_METADATA = [
    {
        "type": "function",
        "function": {
            "name": "tool_get_student_schedule",
            "description": "Tra cuu lich hoc/thoi khoa bieu cua hoc sinh.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day_of_week": {
                        "type": "string",
                        "description": "Thu trong tuan (Thu 2 - Thu 7)",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_school_announcements",
            "description": "Lay thong bao nha truong theo lop hoc hoac toan truong.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_id": {
                        "type": "string",
                        "description": "ID lop hoc, co the bo trong de lay thong bao chung toan truong.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_parent_notifications",
            "description": "Lay cac notification da gui cho phu huynh theo student_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "ID hoc sinh can lay thong bao da gui cho phu huynh.",
                    }
                },
                "required": ["student_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_report_issue_to_teacher",
            "description": "Bao cao thong tin sai hoac gui khieu nai toi giao vien.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_description": {
                        "type": "string",
                        "description": "Noi dung phan hoi",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["wrong_information", "academic_concern", "fee_issue"],
                    },
                },
                "required": ["issue_description"],
            },
        },
    },
]
