try:
    from langchain.agents import AgentExecutor
    print("Imported AgentExecutor from langchain.agents")
except ImportError:
    print("Failed from langchain.agents")

try:
    from langchain.agents.executor import AgentExecutor
    print("Imported AgentExecutor from langchain.agents.executor")
except ImportError:
    print("Failed from langchain.agents.executor")

try:
    from langchain.agents import create_tool_calling_agent
    print("Imported create_tool_calling_agent from langchain.agents")
except ImportError:
    print("Failed from langchain.agents")
