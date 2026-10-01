# 不使用functools.wraps时的问题
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def add(a, b):
    return a + b

import inspect
print(inspect.signature(add))  # 报错！无法获取签名
# 因为wrapper的签名是(*args, **kwargs)，不是原始签名

# 解决方案：使用functools.wraps
import functools
def decorator_fixed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
