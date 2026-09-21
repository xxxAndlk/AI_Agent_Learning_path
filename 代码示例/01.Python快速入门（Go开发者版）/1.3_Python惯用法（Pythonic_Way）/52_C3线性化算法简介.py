# C3线性化示例
class Base:
    def process(self):
        print("Base process")

class Module1(Base):
    def process(self):
        print("Module1 process")
        super().process()  # 调用MRO中下一个类的方法

class Module2(Base):
    def process(self):
        print("Module2 process")
        super().process()

class Service(Module1, Module2):
    def process(self):
        print("Service process")
        super().process()

# MRO顺序: Service -> Module1 -> Module2 -> Base -> object
print(Service.__mro__)

s = Service()
s.process()
# 输出:
# Service process
# Module1 process
# Module2 process
# Base process
