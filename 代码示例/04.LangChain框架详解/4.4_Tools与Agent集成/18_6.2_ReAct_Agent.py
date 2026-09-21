from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 创建工具
@tool
def search_knowledge(query: str) -> str:
    """搜索知识库"""
    knowledge = {
        "python": "Python是一种高级编程语言，由Guido van Rossum创建",
        "java": "Java是一种面向对象的编程语言，由Sun Microsystems开发",
        "javascript": "JavaScript是一种脚本语言，主要用于网页开发"
    }
    for key, value in knowledge.items():
        if key in query.lower():
            return value
    return "未找到相关信息"

@tool
def get_current_date() -> str:
    """获取当前日期"""
    from datetime import datetime
    return datetime.now().strftime("%Y年%m月%d日")

llm = ChatOpenAI(model="gpt-5.4", temperature=0)

# 使用 create_agent 创建Agent（v1.x 推荐）
agent = create_agent(
    model=llm,
    tools=[search_knowledge, get_current_date],
    system_prompt="你是一个智能助手，可以使用工具帮助用户解答各种问题。"
)

# 执行
result = agent.invoke({"messages": [{"role": "user", "content": "今天的日期是什么？请查找关于Python的信息"}]})
print(result["messages"][-1].content)
