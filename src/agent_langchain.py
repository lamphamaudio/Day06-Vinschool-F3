import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from tools import tools
import database

def get_langchain_agent_executor(api_key):
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là trợ lý AI thông minh hỗ trợ phụ huynh trường VinSchool.
        Dưới đây là thông tin bảo mật về học sinh mà bạn đang hỗ trợ. Bạn CHỈ ĐƯỢC PHÉP trả lời và sử dụng Tools cho học sinh này.
        - Tên học sinh: {student_name}
        - Lớp: {class_name}
        - Student ID: {student_id}
        - Class ID: {class_id}
        - Parent ID: {parent_id}
        
        NGUYÊN TẮC:
        1. Luôn sử dụng đúng các ID được cung cấp ở trên khi gọi Tools.
        2. Nếu phụ huynh hỏi về học sinh khác, hãy từ chối lịch sự.
        3. Trả lời tích cực, chuyên nghiệp và ngắn gọn.
        4. Sử dụng tiếng Việt.
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

def call_langchain_agent(api_key, query, session_state):
    student_data = session_state.get("student_data", {}).get("student", {})
    parent_info = session_state.get("parent_info", {})
    
    student_id = student_data.get("student_id")
    class_id = student_data.get("class_id")
    class_name = student_data.get("class_name")
    student_name = student_data.get("full_name")
    parent_id = parent_info.get("parent_id")

    if not student_id or not parent_id:
        return "Vui lòng đăng nhập lại."

    # Khởi tạo hoặc lấy lịch sử chat từ session_state
    chat_history = []
    for msg in session_state.get("messages", [])[-5:]: # Lấy 5 tin nhắn gần nhất
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        else:
            chat_history.append(AIMessage(content=msg["content"]))

    executor = get_langchain_agent_executor(api_key)
    
    try:
        response = executor.invoke({
            "input": query,
            "chat_history": chat_history,
            "student_id": student_id,
            "class_id": class_id,
            "parent_id": parent_id,
            "student_name": student_name,
            "class_name": class_name
        })
        
        final_answer = response["output"]
        
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
        
        return final_answer
    except Exception as e:
        print(f"LangChain Error: {e}")
        return f"Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}"
