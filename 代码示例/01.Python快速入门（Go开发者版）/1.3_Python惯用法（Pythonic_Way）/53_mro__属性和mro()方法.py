class A:
    pass

class B(A):
    pass

class C(A):
    pass

class D(B, C):
    pass

# 方式1：通过__mro__属性（元组）
print(D.__mro__)
# (<class '__main__.D'>, <class '__main__.B'>, 
#  <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)

# 方式2：通过mro()方法（列表）
print(D.mro())
# [__main__.D, __main__.B, __main__.C, __main__.A, <class 'object'>]

# 用于任何类
print(A.mro())
# [<class '__main__.A'>, <class 'object'>]
