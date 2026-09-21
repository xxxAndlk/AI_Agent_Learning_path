# 危险：装饰器工厂函数中使用了可变默认参数
def retry(max_attempts=3, errors=[], delay=1):  # 危险！
    def decorator(func):
        def wrapper(*args, **kwargs):
            # ...
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 正确写法
def retry(max_attempts=3, delay=1, errors=None):
    if errors is None:
        errors = []
    # ...
