class Calculator:
    # 实例方法装饰器
    @staticmethod
    def add(a, b):  # @staticmethod无需self
        return a + b
    
    @classmethod
    def create(cls):  # @classmethod接收cls，不是self
        return cls()
    
    @property
    def value(self):  # @property将方法转为属性
        return self._value

# 常见错误：静态方法不使用staticmethod
class Wrong:
    def add(a, b):  # 缺少@staticmethod
        return a + b

obj = Wrong()
print(obj.add(1, 2))  # 需要实例调用，但语义上是静态的
