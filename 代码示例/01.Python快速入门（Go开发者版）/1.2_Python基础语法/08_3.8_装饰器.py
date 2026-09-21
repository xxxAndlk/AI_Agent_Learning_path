# ============ 装饰器基础（对比Go） ============
# Go没有装饰器，通常使用中间件模式实现类似功能
# Python的装饰器本质是一个高阶函数

# 简单装饰器结构
# 装饰器接收一个函数作为参数，返回一个新函数
def my_decorator(func):
    """装饰器函数：接收被装饰的函数作为参数"""
    def wrapper(*args, **kwargs):
        """包装函数：在原函数执行前后添加额外逻辑"""
        print("调用前执行")
        result = func(*args, **kwargs)  # 调用原函数
        print("调用后执行")
        return result
    return wrapper  # 返回包装后的函数

@my_decorator          # 等价于: say_hello = my_decorator(say_hello)
def say_hello():
    """被装饰的函数"""
    print("Hello!")

# 调用
say_hello()
# 输出:
# 调用前执行
# Hello!
# 调用后执行

# ============ @语法详解 ============
# @装饰器 语法糖等价于:
# 1. 先定义被装饰函数
# 2. 将函数名作为参数传给装饰器
# 3. 用返回值替换原函数名

# 原始写法（不用@语法）
def original_func():
    pass

def decorated_func():
    pass

original_func = my_decorator(original_func)  # 不推荐
decorated_func = my_decorator(decorated_func)  # 不推荐

# @语法写法（推荐）
@my_decorator
def original_func():
    pass
