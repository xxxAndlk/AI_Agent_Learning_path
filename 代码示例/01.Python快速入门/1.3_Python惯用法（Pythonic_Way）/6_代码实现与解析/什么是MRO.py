# MRO是Python多重继承中方法查找的顺序
class A:
    def greet(self):
        print("Hello from A")

class B(A):
    def greet(self):
        print("Hello from B")

class C(A):
    def greet(self):
        print("Hello from C")

class D(B, C):  # 继承自B和C
    pass

d = D()
d.greet()  # 调用哪个 greet？
print(D.__mro__)  # 查看MRO
