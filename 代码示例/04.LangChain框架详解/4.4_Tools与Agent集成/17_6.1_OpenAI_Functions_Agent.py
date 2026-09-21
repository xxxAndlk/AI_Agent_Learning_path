from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 定义工具（v1.x 推荐使用 @tool 装饰器）
@tool
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        allowed_chars = set('0123456789+-*/.() ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return str(result)
        return "表达式包含非法字符"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    weather_data = {
        "北京": "晴，15°C",
        "上海": "多云，20°C",
        "广州": "雨，25°C"
    }
    return weather_data.get(city, f"{city}的天气未知")

# 初始化LLM
llm = ChatOpenAI(model="gpt-5.4", temperature=0)

# 创建Agent（v1.x 推荐方式）
tools = [calculator, get_weather]
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个有用的AI助手，可以使用工具帮助用户解决问题。"
)

# 执行查询
result = agent.invoke({"messages": [{"role": "user", "content": "北京今天天气怎么样？请计算一下15+25的结果"}]})
print(result["messages"][-1].content)
