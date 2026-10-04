"""
完整Agent链实现示例（v1.x 推荐方式）
展示如何使用 create_agent 构建智能Agent
"""

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

# ============================================================
# 步骤1：定义工具
# ============================================================

@tool
def search_knowledge_base(query: str) -> str:
    """搜索知识库获取相关信息。适用于需要查询特定知识或事实的问题。"""
    # 实际项目中应该连接真实的知识库
    knowledge = {
        "python": "Python是一种高级编程语言，由Guido van Rossum创建。",
        "javascript": "JavaScript是一种脚本语言，主要用于Web开发。",
        "java": "Java是一种面向对象的编程语言，特点是'一次编写，到处运行'。"
    }
    
    for key, value in knowledge.items():
        if key in query.lower():
            return value
    
    return "未找到相关信息"

@tool
def calculate(expression: str) -> float:
    """数学计算器。适用于需要计算数学表达式的问题。"""
    try:
        # 注意：生产环境应该使用安全的计算方式
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含非法字符"
        
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{str(e)}"

@tool
def get_current_time() -> str:
    """获取当前时间。适用于询问当前时间或日期的问题。"""
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")

# 收集所有工具
tools = [search_knowledge_base, calculate, get_current_time]

# ============================================================
# 步骤2：创建LLM和Agent（v1.x 推荐方式）
# ============================================================

# 创建支持工具调用的LLM
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0
)

# 使用 create_agent 创建基于 LangGraph 的Agent（v1.x 推荐）
# 替代了旧版的 create_openai_functions_agent + AgentExecutor 组合
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""你是一个智能助手，可以帮助用户解答各种问题。

可用的工具：
- search_knowledge_base: 搜索知识库
- calculate: 数学计算
- get_current_time: 获取当前时间

当用户的问题涉及以上方面时，你应该主动使用相应的工具。
回答要简洁、准确。"""
)

# ============================================================
# 步骤3：测试Agent
# ============================================================

# 测试问题1：需要搜索知识库
print("=" * 50)
print("测试1：搜索知识库")
result = agent.invoke({
    "messages": [{"role": "user", "content": "Python是什么时候创建的？"}]
})
print(f"回答：{result['messages'][-1].content}")

# 测试问题2：需要计算
print("\n" + "=" * 50)
print("测试2：数学计算")
result = agent.invoke({
    "messages": [{"role": "user", "content": "计算 (15 + 25) * 3 / 10"}]
})
print(f"回答：{result['messages'][-1].content}")

# 测试问题3：需要获取时间
print("\n" + "=" * 50)
print("测试3：获取时间")
result = agent.invoke({
    "messages": [{"role": "user", "content": "现在是什么时候？"}]
})
print(f"回答：{result['messages'][-1].content}")

# 测试问题4：普通问答
print("\n" + "=" * 50)
print("测试4：普通问答")
result = agent.invoke({
    "messages": [{"role": "user", "content": "你好，请介绍一下你自己"}]
})
print(f"回答：{result['messages'][-1].content}")
