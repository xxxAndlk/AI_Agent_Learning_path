# ============ 函数定义（对比Go） ============
# Go:
# func add(a int, b int) int {
#     return a + b
# }

# Python:
def add(a, b):          # 不需要声明参数类型和返回值类型
    """函数文档字符串（docstring），类似Go的函数注释"""
    return a + b

# 调用（和Go一样）
result = add(3, 5)

# 多返回值（Go的特色，Python用元组模拟）
# Go: func divide(a, b float64) (float64, error)
# Python:
def divide(a, b):
    if b == 0:
        return None, "除数不能为零"    # 返回多个值（实际是元组）
    return a / b, None

quotient, err = divide(10, 2)
if err:
    print(f"错误: {err}")
else:
    print(f"结果: {quotient}")

# 默认参数值（Go不支持，Python支持）
def greet(name, greeting="你好"):
    return f"{greeting}, {name}!"

print(greet("张三"))              # 输出: 你好, 张三!
print(greet("李四", "早上好"))     # 输出: 早上好, 李四!

# 可变参数（类似Go的...）
# Go: func sum(nums ...int) int
# Python:
def sum_all(*nums):     # *nums收集所有位置参数为元组
    total = 0
    for num in nums:
        total += num
    return total

print(sum_all(1, 2, 3, 4))      # 输出: 10

# 关键字参数（Go不支持）
def create_user(name, age, **kwargs):   # **kwargs收集所有关键字参数为字典
    user = {"name": name, "age": age}
    user.update(kwargs)
    return user

user = create_user("张三", 25, city="北京", email="zs@example.com")
