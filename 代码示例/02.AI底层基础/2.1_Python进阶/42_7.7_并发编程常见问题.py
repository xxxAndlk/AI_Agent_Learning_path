# 问题：无法传递不可序列化对象
class Unpickleable:
    def __init__(self):
        self.func = lambda: 1  # 闭包不可pickle

# 解决方案：使用独立函数或cloudpickle库
def pickleable_func(x):
    return x ** 2
