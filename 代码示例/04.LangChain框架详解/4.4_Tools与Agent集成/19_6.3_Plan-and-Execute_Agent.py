from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def search_learning_resource(topic: str) -> str:
    """搜索学习资源"""
    return f"关于 {topic} 的推荐学习资源..."

llm = ChatOpenAI(model="gpt-5.4", temperature=0)

# 使用 create_agent 创建Agent（v1.x 推荐）
agent = create_agent(
    model=llm,
    tools=[search_learning_resource],
    system_prompt="你是一个学习规划助手，可以帮助用户制定学习计划。"
)

# 执行复杂任务
result = agent.invoke({"messages": [{"role": "user", "content": """
请制定一个学习Python机器学习的计划，包括：
1. 需要掌握的基础知识
2. 推荐的学习资源
3. 实践项目建议
4. 学习时间安排
"""}]})
print(result["messages"][-1].content)
