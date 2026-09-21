# 基础装饰器模板
def basic_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 前置处理
        result = func(*args, **kwargs)
        # 后置处理
        return result
    return wrapper

# 带参数装饰器模板
def param_decorator(param):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 使用param进行配置
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

# 类装饰器模板
class ClassDecorator:
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args, **kwargs):
        # 可维护状态
        return self.func(*args, **kwargs)
