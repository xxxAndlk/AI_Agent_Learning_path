"""
LangChain Agent实现示例（v1.x 推荐方式）
演示如何使用 create_agent 创建能自主调用工具的AI智能体
"""

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
import math

# ============================================================
# 步骤1：使用 @tool 装饰器定义工具（v1.x 推荐方式）
# ============================================================
@tool
def search_web(query: str) -> str:
    """当需要查询最新信息、新闻或不确定的知识时使用"""
    # 这里使用模拟数据，实际应调用搜索API
    return f"搜索结果：关于'{query}'找到相关信息..."

@tool
def calculate(expression: str) -> str:
    """当需要进行数学计算时使用，支持加减乘除和括号"""
    try:
        # 白名单允许的字符，防止代码注入
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含非法字符"
        
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

@tool
def get_weather(city: str) -> str:
    """当需要查询某个城市的天气时使用，输入城市名"""
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，28°C",
        "广州": "小雨，30°C"
    }
    return weather_data.get(city, f"未找到{city}的天气信息")

# 收集所有工具
tools = [search_web, calculate, get_weather]

# ============================================================
# 步骤2：创建LLM实例
# ============================================================
# Agent需要支持function calling的模型
# OpenAI的gpt-5.4-mini和gpt-5.4都支持
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0  # Agent通常使用确定性输出
)

# ============================================================
# 步骤3：使用 create_agent 创建Agent（v1.x 推荐）
# ============================================================
# create_agent 是 v1.x 中一键创建基于 LangGraph 的生产级 Agent 的工厂函数
# 替代了旧版的 create_openai_functions_agent + AgentExecutor 组合
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个有用的AI助手，可以使用工具帮助用户解决问题。"
)

# ============================================================
# 步骤4：执行Agent
# ============================================================
# Agent会自动分析用户意图，决定是否需要调用工具
# 并自主完成多步骤任务
response = agent.invoke({
    "messages": [{"role": "user", "content": "计算 1234 * 5678 是多少，并告诉我上海的天气"}]
})

print(f"最终回答：{response['messages'][-1].content}")

# ============================================================
# 迁移说明：
# v0.x / 旧版 v1.x 中使用的方式：
#   from langchain.agents import AgentExecutor, create_openai_functions_agent
#   agent = create_openai_functions_agent(llm, tools, prompt)
#   agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
#   result = agent_executor.invoke({"input": "..."})
#
# v1.x 新方式（推荐）：
#   from langchain.agents import create_agent
#   agent = create_agent(model=llm, tools=tools, system_prompt="...")
#   result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
# ============================================================
