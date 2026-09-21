# 问题代码
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def add(a, b):
    """Add two numbers"""
    return a + b

print(add.__name__)  # 输出: wrapper（丢失了原函数名）
print(add.__doc__)   # 输出: None（丢失了文档字符串）

# 解决方案：使用@wraps
from functools import wraps

def decorator(func):
    @wraps(func)  # 保留原函数元数据
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
