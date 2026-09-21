"""
高阶函数和反射 - 对比Go的reflect包
"""

import functools
import inspect
from collections import namedtuple

# ============ functools - 函数式编程工具 ============
# Go: 需要自行实现或使用第三方库

# @lru_cache - 缓存函数调用结果
# Go: 手动实现缓存或使用golang-lru
@functools.lru_cache(maxsize=128)
def fibonacci(n):
    """斐波那契数列（带缓存）"""
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(f"Fibonacci(100): {fibonacci(100)}")  # 快速返回缓存结果
print(f"缓存信息: {fibonacci.cache_info()}")

# clear_cache清除缓存
# fibonacci.cache_clear()

# @total_ordering - 自动实现比较方法
@functools.total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.major, self.minor, self.patch = major, minor, patch
    
    def __eq__(self, other):
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

v1, v2 = Version(1, 2, 3), Version(1, 2, 4)
print(f"v1 < v2: {v1 < v2}")  # True（自动生成>, <=, >=）

# partial - 部分应用（冻结部分参数）
# Go: 需要手动实现函数闭包
def power(base, exponent):
    return base ** exponent

square = functools.partial(power, exponent=2)  # 固定exponent=2
cube = functools.partial(power, exponent=3)

print(f"5^2 = {square(5)}")   # 25
print(f"5^3 = {cube(5)}")     # 125

# reduce - 归约（类似Go的reduce）
# Go: 手动循环实现
result = functools.reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])  # 15
print(f"Sum: {result}")

# reduce带初始值
result = functools.reduce(lambda x, y: x + y, [1, 2, 3], 10)  # 16

# cached_property - 属性缓存（Python 3.8+）
class DataProcessor:
    @functools.cached_property
    def expensive_result(self):
        """计算昂贵的属性（只计算一次）"""
        print("计算中...")
        return sum(range(10000))

dp = DataProcessor()
print(dp.expensive_result)  # 第一次计算并缓存
print(dp.expensive_result)  # 直接返回缓存值

# singledispatch - 函数重载（单分派）
@functools.singledispatch
def process(data):
    """默认处理"""
    return f"处理数据: {data}"

@process.register(int)
def _(data):
    return f"整数: {data * 2}"

@process.register(str)
def _(data):
    return f"字符串: {data.upper()}"

print(process(42))      # 调用int版本
print(process("hello")) # 调用str版本

# ============ inspect - 运行时反射 ============
# Go: reflect包

# 获取函数信息
# Go: runtime.Func.Name()
def example_function(a, b, c=10):
    """示例函数"""
    pass

print(f"函数名: {inspect.signature(example_function)}")
print(f"函数签名: {inspect.signature(example_function)}")
print(f"函数文档: {inspect.getdoc(example_function)}")

# 获取函数参数信息
sig = inspect.signature(example_function)
for name, param in sig.parameters.items():
    print(f"  参数: {name}, 类型: {param.annotation}, 默认值: {param.default}")

# 检查对象类型
# Go: reflect.TypeOf()
class MyClass:
    pass

obj = MyClass()
print(f"类型名: {type(obj).__name__}")  # MyClass
print(f"模块: {inspect.getmodule(obj)}")

# 获取类的成员
print(f"类方法: {[m for m in dir(obj) if not m.startswith('_')]}")

# 检查函数是否可以调用
print(f"可调用: {callable(example_function)}")

# 获取源代码
try:
    source = inspect.getsource(example_function)
    print(f"源代码:\n{source}")
except OSError:
    print("无法获取源代码（可能已编译）")

# 获取调用栈
def inner_function():
    """内部函数"""
    for frame in inspect.stack():
        print(f"调用: {frame.function} at {frame.filename}:{frame.lineno}")

def outer_function():
    inner_function()

outer_function()

# 检查装饰器
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def decorated_func():
    """被装饰的函数"""
    pass

print(f"原函数: {inspect.get原函数(decorated_func)}")  # wrapped
print(f"包装函数: {decorated_func.__wrapped__}")  # 原函数
