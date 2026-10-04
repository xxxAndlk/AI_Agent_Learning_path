from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from datetime import datetime, timedelta

# ==================== 工具定义 ====================

@tool
def get_current_datetime(format: str = "full") -> str:
    """获取当前日期时间
    
    Args:
        format: 输出格式 full/date/time
    """
    now = datetime.now()
    if format == "date":
        return now.strftime("%Y年%m月%d日")
    elif format == "time":
        return now.strftime("%H:%M:%S")
    return now.strftime("%Y年%m月%d日 %H:%M:%S")

@tool
def calculate_date(start_date: str, days: int, operation: str = "add") -> str:
    """日期计算器
    
    Args:
        start_date: 起始日期 (YYYY-MM-DD)
        days: 天数
        operation: add/subtract
    """
    try:
        date = datetime.strptime(start_date, "%Y-%m-%d")
        if operation == "add":
            result = date + timedelta(days=days)
        else:
            result = date - timedelta(days=days)
        return result.strftime("%Y年%m月%d日")
    except Exception as e:
        return f"日期格式错误: {e}"

@tool
def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """单位转换器
    
    Args:
        value: 数值
        from_unit: 源单位
        to_unit: 目标单位
    """
    conversions = {
        ("km", "miles"): 0.621371,
        ("miles", "km"): 1.60934,
        ("kg", "pounds"): 2.20462,
        ("pounds", "kg"): 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return f"不支持的转换: {from_unit} -> {to_unit}"
    
    factor = conversions[key]
    if callable(factor):
        result = factor(value)
    else:
        result = value * factor
    
    return f"{value} {from_unit} = {result:.2f} {to_unit}"

@tool
def generate_code_snippet(language: str, task: str) -> str:
    """生成代码片段
    
    Args:
        language: 编程语言
        task: 任务描述
    """
    templates = {
        "python": {
            "hello": 'print("Hello, World!")',
            "function": 'def function_name(params):\n    # 你的代码\n    pass',
            "class": 'class ClassName:\n    def __init__(self):\n        pass',
        },
        "javascript": {
            "hello": 'console.log("Hello, World!");',
            "function": 'function functionName(params) {\n    // 你的代码\n}',
        }
    }
    
    lang_templates = templates.get(language.lower(), {})
    snippet = lang_templates.get(task.lower())
    
    if snippet:
        return f"```{language.lower()}\n{snippet}\n```"
    
    return f"我理解你想用{language}实现{task}，这是基本框架:\n```{language.lower()}\n# 你的代码\n```"

# ==================== Agent配置 ====================

tools = [
    get_current_datetime,
    calculate_date,
    unit_converter,
    generate_code_snippet
]

llm = ChatOpenAI(model="gpt-5.4", temperature=0.3)

# 使用 create_agent 创建Agent（v1.x 推荐）
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""你是一个多功能助手，能够帮助用户完成各种任务：

可用的能力：
1. 日期时间查询 - 问现在几点、今天几号
2. 日期计算 - 加减天数
3. 单位转换 - 长度、重量、温度等
4. 代码生成 - 生成各种编程语言的代码片段

请根据用户的需求，选择合适的工具来完成任务。
如果用户没有明确说明，使用最合适的工具。
"""
)

# ==================== 使用示例 ====================

def chat(user_input: str):
    """聊天接口"""
    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    return result["messages"][-1].content

# 测试
if __name__ == "__main__":
    print(chat("现在几点了？"))
    print("\n" + "-"*40)
    print(chat("100公里等于多少英里？"))
    print("\n" + "-"*40)
    print(chat("生成一个Python函数"))
    print("\n" + "-"*40)
    print(chat("2024年1月1日加上100天是哪天？"))
