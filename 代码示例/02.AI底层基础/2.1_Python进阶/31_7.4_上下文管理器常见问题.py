# 问题代码
class Resource:
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("清理资源")
        # 异常被吞掉了！

# 解决方案：正确处理异常
class Resource:
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("清理资源")
        return False  # 传播异常
        # 或 return True  抑制异常
