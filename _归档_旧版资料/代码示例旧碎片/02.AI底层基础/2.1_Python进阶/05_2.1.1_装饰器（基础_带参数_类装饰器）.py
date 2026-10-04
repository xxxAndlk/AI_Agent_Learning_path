import time                           # 导入时间模块，用于计算函数执行时间
from functools import wraps           # 导入wraps装饰器，用于保留被装饰函数的元数据

# ============ 1. 基础装饰器：计时功能 ============
def timer(func):
    """计时装饰器：测量并打印函数执行时间"""
    @wraps(func)                      # 使用@wraps保留原函数的__name__和__doc__
    def wrapper(*args, **kwargs):     # 定义包装函数，接收任意位置参数和关键字参数
        start = time.time()           # 记录函数开始执行的时间戳
        result = func(*args, **kwargs) # 调用被装饰的原始函数，传入所有参数
        end = time.time()             # 记录函数执行结束的时间戳
        # 打印函数名和执行耗时，:.4f表示保留4位小数
        print(f"[{func.__name__}] 运行耗时: {end - start:.4f}s")
        return result                 # 返回原始函数的执行结果
    return wrapper                    # 返回包装函数，替换原始函数

# ============ 2. 带参数的装饰器：重复执行 ============
def repeat(times: int):
    """带参数的装饰器：让函数重复执行指定次数"""
    def decorator(func):              # 真正的装饰器函数，接收被装饰的函数
        @wraps(func)                  # 保留原函数元数据
        def wrapper(*args, **kwargs): # 包装函数
            results = []              # 创建空列表，存储每次执行的结果
            for _ in range(times):    # 循环指定次数（times参数来自外层）
                results.append(func(*args, **kwargs)) # 调用函数并将结果添加到列表
            return results            # 返回包含所有结果的列表
        return wrapper                # 返回包装函数
    return decorator                  # 返回装饰器函数

# ============ 3. 类装饰器：日志记录 ============
class Logger:
    """类装饰器：使用类来实现装饰器功能，记录函数调用信息"""
    def __init__(self, func):
        """构造函数，接收被装饰的函数"""
        wraps(func)(self)             # 使用wraps将原函数的元数据复制到实例
        self.func = func              # 保存被装饰的函数引用
    
    def __call__(self, *args, **kwargs):
        """使实例可调用，当执行 func() 时会调用此方法"""
        # 打印函数名和传入的参数信息
        print(f"调用函数: {self.func.__name__} | 参数: {args} {kwargs}")
        return self.func(*args, **kwargs) # 调用原始函数并返回结果

# ============ 装饰器的堆叠使用 ============
@timer                              # 第3层：计时（最后执行，最先包装）
@repeat(times=3)                    # 第2层：重复执行3次
@Logger                             # 第1层：日志记录（最先执行，最后包装）
def calculate_sum(n: int):
    """计算从0到n-1的所有整数之和"""
    return sum(range(n))            # 使用内置sum函数计算总和

# ============ 主程序入口 ============
if __name__ == "__main__":          # 确保以下代码只在直接运行文件时执行
    calculate_sum(1000000)          # 调用被装饰的函数，传入100万作为参数
