from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 定义多个互补的工具
@tool
def search_docs(query: str) -> str:
    """搜索官方文档。适用于：技术问题、API使用、框架功能查询"""
    docs = {
        "python": "Python官方文档: docs.python.org",
        "langchain": "LangChain文档: python.langchain.com",
        "openai": "OpenAI文档: platform.openai.com"
    }
    for key, value in docs.items():
        if key in query.lower():
            return value
    return "未找到相关文档"

@tool
def search_github(query: str) -> str:
    """搜索GitHub代码库。适用于：查找示例代码、项目实现、bug修复"""
    return f"GitHub搜索结果: {query}相关项目"

@tool
def search_stackoverflow(query: str) -> str:
    """搜索Stack Overflow。适用于：常见问题、错误解决、具体问题解答"""
    return f"Stack Overflow结果: {query}相关的问答"

# 使用 create_agent 创建Agent（v1.x 推荐）
llm = ChatOpenAI(model="gpt-5.4", temperature=0)
agent = create_agent(
    model=llm,
    tools=[search_docs, search_github, search_stackoverflow],
    system_prompt="你是一个技术助手，可以根据用户问题选择合适的搜索工具。"
)

# 测试不同类型的查询
result1 = agent.invoke({"messages": [{"role": "user", "content": "如何在Python中使用装饰器？"}]})
print(result1["output"])
print("\n" + "="*50 + "\n")
result2 = agent.invoke({"messages": [{"role": "user", "content": "查找langchain agent的示例代码"}]})
print(result2["output"])
