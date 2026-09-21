# ============ 变量声明（对比Go） ============
# Go: var name string = "张三" 或 name := "张三"
# Python: 直接赋值，无需声明类型
name = "张三"           # 字符串（对应Go string）
age = 25               # 整数（对应Go int）
height = 1.75          # 浮点数（对应Go float64）
is_student = True      # 布尔值（对应Go bool）

# 查看类型
print(type(name))      # 输出: <class 'str'>

# 多变量赋值（类似Go的平行赋值）
# Go: a, b := 1, 2
a, b = 1, 2

# 常量（Python没有真正的常量，约定用大写）
# Go: const PI = 3.14159
PI = 3.14159           # 约定：全大写表示常量，但仍可修改

# ============ 字符串操作（对比Go） ============
# Go: 字符串不可变，用+连接
# Python: 字符串也不可变，但操作更方便
s = "Hello"

# 字符串拼接
# Go: s1 + s2
# Python: 多种方式
s1 = "Hello" + " " + "World"        # 使用+号
s2 = f"Name: {name}, Age: {age}"    # f-string（推荐，类似Go的fmt.Sprintf）
s3 = "Name: {}, Age: {}".format(name, age)  # format方法

# 字符串切片（和Go的slice语法几乎一样）
# Go: s[0:5]
sub = s[0:5]           # 取前5个字符

# 常用方法
s_upper = s.upper()    # 转大写（类似Go strings.ToUpper）
s_lower = s.lower()    # 转小写
s_len = len(s)         # 长度（类似Go len()）
