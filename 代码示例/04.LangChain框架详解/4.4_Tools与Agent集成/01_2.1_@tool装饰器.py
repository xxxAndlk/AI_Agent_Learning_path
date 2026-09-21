from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b

@tool  
def multiply(a: int, b: int) -> int:
    """计算两个数的乘积"""
    return a * b

# 调用工具
result = add.invoke({"a": 5, "b": 3})  # 返回 8
print(result)
