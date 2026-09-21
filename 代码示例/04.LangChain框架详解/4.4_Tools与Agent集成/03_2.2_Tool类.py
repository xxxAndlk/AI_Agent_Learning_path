from langchain_core.tools import Tool

def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        # 安全的数学表达式计算
        allowed_chars = set('0123456789+-*/.() ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return str(result)
        return "表达式包含非法字符"
    except Exception as e:
        return f"计算错误: {str(e)}"

# 创建Tool对象
calc_tool = Tool(
    name="calculator",
    func=calculate,
    description="用于执行数学计算。支持加减乘除和括号。注意：输入必须是有效的数学表达式。"
)

# 调用工具
result = calc_tool.invoke("2 + 3 * 4")
print(result)  # 输出: 14
