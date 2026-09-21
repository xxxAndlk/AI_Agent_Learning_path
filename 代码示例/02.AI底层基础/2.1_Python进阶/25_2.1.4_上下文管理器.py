import time                                   # 导入时间模块，用于模拟耗时操作

# ============ 1. 类实现上下文管理器 ============
class Timer:
    """计时上下文管理器：测量代码块执行时间
    
    使用with语句自动管理计时开始和结束
    """
    def __init__(self, name: str = "代码块"):
        """初始化计时器
        
        参数:
            name: 要计时的代码块名称
        """
        self.name = name                      # 保存名称，用于输出显示
        self.start_time = None                # 初始化开始时间为None
    
    def __enter__(self):
        """进入上下文时触发，记录开始时间
        
        返回:
            self: 绑定到as后的变量
        """
        self.start_time = time.time()         # 记录当前时间戳作为开始时间
        print(f"[{self.name}] 开始执行...")    # 打印开始提示信息
        return self                           # 返回self，可在with块内使用
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """离开上下文时触发，计算并打印耗时
        
        参数:
            exc_type: 异常类型（如果有）
            exc_val: 异常值（如果有）
            exc_tb: 异常回溯（如果有）
        返回:
            False: 不抑制异常，让异常继续传播
        """
        elapsed = time.time() - self.start_time  # 计算执行耗时
        print(f"[{self.name}] 执行完成，耗时: {elapsed:.4f}秒")  # 打印耗时
        return False                          # 不拦截异常，让异常正常传播

# ============ 2. 函数实现上下文管理器 ============
from contextlib import contextmanager         # 导入contextmanager装饰器

@contextmanager                               # 将生成器函数转换为上下文管理器
def managed_resource(name: str):
    """资源管理上下文管理器：演示函数式实现
    
    使用yield将代码分为enter和exit两部分
    
    参数:
        name: 资源名称
    """
    print(f"[{name}] 获取资源")               # 进入前执行，相当于__enter__
    try:
        yield name                            # yield的值绑定到as后的变量
    finally:
        print(f"[{name}] 释放资源")           # 离开时执行，相当于__exit__

# ============ 3. contextlib实用工具 ============
from contextlib import closing, suppress      # 导入实用工具

class Resource:
    """模拟需要关闭的资源"""
    def close(self):
        print("资源已关闭")

# closing：确保close()被调用
with closing(Resource()) as r:
    print(f"使用资源: {r}")

# suppress：忽略特定异常
with suppress(FileNotFoundError):
        # 如果文件不存在，忽略异常继续执行
        pass

# ============ 主程序入口 ============
if __name__ == "__main__":
    # 使用类实现的上下文管理器
    with Timer("数据处理") as timer:
        # 模拟数据处理耗时
        time.sleep(0.1)
        result = sum(range(10000))
    
    # 使用函数实现的上下文管理器
    with managed_resource("数据库连接") as conn:
        print(f"正在使用 {conn} 进行操作")
    
    # 嵌套使用
    with Timer("外层计时"):
        time.sleep(0.05)
        with Timer("内层计时"):
            time.sleep(0.03)
