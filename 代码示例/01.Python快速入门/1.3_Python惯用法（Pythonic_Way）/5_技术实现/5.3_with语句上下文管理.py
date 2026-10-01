# 上下文管理器协议
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self  # 返回值赋给as后的变量
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end = time.time()
        print(f"耗时: {self.end - self.start:.2f}秒")
        # 返回True会抑制异常，返回False或None会继续传播异常
        return False

# 使用
with Timer() as t:
    # do something
    pass
# 自动调用__exit__，打印耗时
