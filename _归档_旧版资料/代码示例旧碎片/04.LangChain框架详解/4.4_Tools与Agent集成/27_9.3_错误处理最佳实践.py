from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def may_fail_tool(command: str) -> str:
    """可能失败的工具"""
    if command == "fail":
        raise ValueError("故意触发的错误")
    if command == "timeout":
        import time
        time.sleep(35)  # 模拟超时
    return f"成功执行: {command}"

llm = ChatOpenAI(model="gpt-5.4")
agent = create_agent(
    model=llm,
    tools=[may_fail_tool],
    system_prompt="你是一个智能助手，可以使用工具完成任务。"
)

# 测试
try:
    result = agent.invoke({"messages": [{"role": "user", "content": "执行命令 'test'"}]})
    print(result["messages"][-1].content)
except Exception as e:
    print(f"执行异常: {e}")
