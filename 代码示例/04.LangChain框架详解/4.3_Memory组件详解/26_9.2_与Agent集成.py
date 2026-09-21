from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(model="gpt-5.4-mini")

# 定义工具（v1.x 推荐使用 @tool 装饰器）
@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        return str(eval(expression))
    except:
        return "0"

@tool
def get_weather(city: str) -> str:
    """查询城市天气"""
    weather_data = {
        "北京": "晴，25°C",
        "上海": "多云，28°C",
        "广州": "雨，30°C"
    }
    return weather_data.get(city, "未知")

tools = [calculate, get_weather]

# 创建带Memory的Agent（v1.x：通过 checkpointer 持久化对话状态实现跨轮记忆；
# 旧版 ConversationBufferWindowMemory 属 v0.x 范式，不能直接传给 create_agent）
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个有帮助的AI助手，可以使用工具完成任务。",
    checkpointer=InMemorySaver(),
)

# 对话
dialogues = [
    "北京今天天气怎么样？",
    "帮我计算一下 123 * 456",
    "我刚才问了什么？"
]

for user_input in dialogues:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": "demo-user"}},
    )
    print(f"\n用户: {user_input}")
    print(f"Agent: {result['messages'][-1].content}")
