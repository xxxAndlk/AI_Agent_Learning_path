# Python类的核心概念
class MyClass:
    class_var = "shared"        # 类变量（类似Go的包级变量）
    
    def __init__(self, value):   # 构造函数
        self.instance_var = value  # 实例变量
    
    def method(self):            # 实例方法
        pass
    
    @classmethod
    def cls_method(cls):         # 类方法
        pass
    
    @staticmethod
    def static_method():         # 静态方法
        pass
