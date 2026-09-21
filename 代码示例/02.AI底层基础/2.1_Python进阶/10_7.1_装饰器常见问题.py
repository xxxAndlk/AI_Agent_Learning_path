# 问题：类装饰器无法正确处理实例方法
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

class MyClass:
    @CountCalls  # ❌ self不会正确传递
    def method(self):
        pass

# 解决方案：使用函数装饰器或正确处理self
def count_calls(func):
    count = 0
    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal count
        count += 1
        return func(*args, **kwargs)
    wrapper.count = lambda: count
    return wrapper
