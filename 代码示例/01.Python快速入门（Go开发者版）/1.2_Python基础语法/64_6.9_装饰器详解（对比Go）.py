# ============ 带参数的装饰器 ============
# 之前的装饰器不带参数，如果需要装饰器接受参数，需要再包装一层

def repeat(times):              # 第1层：接收装饰器参数
    """重复执行指定次数的装饰器"""
    def decorator(func):       # 第2层：接收被装饰函数
        def wrapper(*args, **kwargs):  # 第3层：包装函数
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)               # 先调用repeat(3)，返回decorator
def greet(name):
    print(f"Hello, {name}!")

greet("张三")
# 输出:
# Hello, 张三!
# Hello, 张三!
# Hello, 张三!

# ============ functools.wraps 保持元信息 ============
# 问题：不使用wraps时，原函数的__name__、__doc__等会被覆盖

def simple_decorator(func):
    def wrapper(*args, **kwargs):
        """我是wrapper的文档"""
        return func(*args, **kwargs)
    return wrapper

@simple_decorator
def example():
    """我是example的文档"""
    pass

print(example.__name__)  # 输出: wrapper（错误！应该是example）
print(example.__doc__)   # 输出: 我是wrapper的文档（错误！）

# 解决方案：使用functools.wraps
import functools

def proper_decorator(func):
    @functools.wraps(func)  # 复制原函数的元信息到wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@proper_decorator
def example2():
    """我是example2的文档"""
    pass

print(example2.__name__)  # 输出: example2（正确！）
print(example2.__doc__)   # 输出: 我是example2的文档（正确！）

# ============ 类装饰器 ============
# 装饰器不仅可以用于函数，也可以用于类

def singleton(cls):
    """单例模式装饰器：确保类只有一个实例"""
    instances = {}  # 存储实例的字典
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class Database:
    def __init__(self):
        print("创建数据库连接")
    
    def query(self, sql):
        return f"执行: {sql}"

# 测试单例
db1 = Database()  # 输出: 创建数据库连接
db2 = Database()  # 不再创建新实例
print(db1 is db2)  # 输出: True（同一个实例）

# 类方法装饰器（Python内置）
class Math:
    @staticmethod
    def add(a, b):     # 静态方法：不需要self/cls
        return a + b
    
    @classmethod
    def multiply(cls, a, b):  # 类方法：接收cls作为第一个参数
        return a * b

# ============ 多装饰器叠加 ============
# 多个装饰器可以叠加使用，执行顺序从下到上

def decorator_a(func):
    """装饰器A"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("A前")
        result = func(*args, **kwargs)
        print("A后")
        return result
    return wrapper

def decorator_b(func):
    """装饰器B"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("B前")
        result = func(*args, **kwargs)
        print("B后")
        return result
    return wrapper

@decorator_a  # 先应用B，再应用A
@decorator_b
def process():
    print("处理中")

process()
# 输出:
# A前
# B前
# 处理中
# B后
# A后

# 等价于: process = decorator_a(decorator_b(process))
# 执行顺序: decorator_a(decorator_b(process))()
# 即: 外层A先执行前序，内层B后执行前序，原函数，然后B后执行，最后A后执行
