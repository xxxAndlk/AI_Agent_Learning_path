# ============ 变量声明 ============
# 直接赋值，无需声明类型
name = "张三"           # 字符串
age = 25               # 整数
height = 1.75          # 浮点数
is_student = True      # 布尔值

# 查看类型
print(type(name))      # 输出: <class 'str'>

# 多变量赋值
a, b = 1, 2

# 常量（Python没有真正的常量，约定用大写）
PI = 3.14159           # 约定：全大写表示常量，但仍可修改

# ============ 字符串操作 ============
# 字符串也不可变，但操作更方便
s = "Hello"

# 字符串拼接
# 多种方式
s1 = "Hello" + " " + "World"        # 使用+号
s2 = f"Name: {name}, Age: {age}"    # f-string
s3 = "Name: {}, Age: {}".format(name, age)  # format方法

# 字符串切片
sub = s[0:5]           # 取前5个字符

# 常用方法
s_upper = s.upper()    # 转大写
s_lower = s.lower()    # 转小写
s_len = len(s)         # 长度
