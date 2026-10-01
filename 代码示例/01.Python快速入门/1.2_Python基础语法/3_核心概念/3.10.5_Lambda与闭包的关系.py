# ============ Lambda闭包详解 ============

# 闭包是指函数能够捕获并记住其定义时所在作用域中的变量

# 1. 基本的闭包捕获
def outer():
    x = 10  # 外层变量
    
    # lambda捕获外层变量x
    # 注意：捕获的是变量的引用，不是值
    inner = lambda: x + 1
    
    x = 20  # 修改外层变量
    return inner

# 调用outer()得到inner函数
# inner捕获了x的引用，所以返回20+1=21，而不是11
f = outer()
print(f())  # 输出: 21

# 2. 延迟绑定问题（重要！）
# 这是Lambda闭包中最常见的陷阱
funcs = [lambda: i for i in range(3)]  # 创建3个lambda

# 遍历执行，每个都返回2，而不是0,1,2
for f in funcs:
    print(f(), end=" ")  # 输出: 2 2 2

print()

# 3. 解决延迟绑定：使用默认参数捕获当前值
# 默认参数在函数定义时求值，可以"冻结"当前值
funcs_fixed = [lambda i=i: i for i in range(3)]

for f in funcs_fixed:
    print(f(), end=" ")  # 输出: 0 1 2

print()

# 4. 实际应用：创建带参数的闭包工厂
def make_multiplier(factor):
    """创建乘法器闭包"""
    return lambda x: x * factor

# 创建不同的乘法器
times2 = make_multiplier(2)
times3 = make_multiplier(3)
times10 = make_multiplier(10)

print(times2(5))   # 10
print(times3(5))   # 15
print(times10(5))  # 50
