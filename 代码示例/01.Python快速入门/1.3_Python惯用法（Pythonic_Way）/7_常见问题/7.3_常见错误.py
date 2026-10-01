# 错误1：在推导式中修改外部变量
x = 0
[x := x + 1 for _ in range(10)]  # Python 3.8+，但不推荐

# 正确做法
x = sum(1 for _ in range(10))

# 错误2：误解链式比较
x = 5
print(x < 6 > 4)  # True，等价于 x < 6 and 6 > 4
print(x < 6 and x > 4)  # True
print(4 < x < 6)  # True，这才是检查x在(4,6)区间

# 错误3：混淆 is 和 ==
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True，值相等
print(a is b)  # False，不是同一对象

# is 用于身份比较，== 用于值比较
# is 用于 None, True, False 检查
# if x is None:  # 正确写法
# if x == None:  # 不推荐，应使用is
