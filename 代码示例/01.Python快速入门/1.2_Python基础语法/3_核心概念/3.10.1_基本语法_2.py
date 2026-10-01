# 最简单的Lambda：没有参数，返回固定值
# 等价于: def get_five(): return 5
get_five = lambda: 5           # 定义返回5的Lambda表达式
print(get_five())              # 输出: 5

# 带一个参数的Lambda
# 等价于: def square(x): return x * x
square = lambda x: x * x       # 计算x的平方
print(square(4))               # 输出: 16

# 带两个参数的Lambda
# 等价于: def add(a, b): return a + b
add = lambda a, b: a + b       # 两个数相加
print(add(3, 5))               # 输出: 8

# 多参数的Lambda
# 等价于: def greet(name, greeting): return f"{greeting}, {name}!"
greet = lambda name, greeting: f"{greeting}, {name}!"
print(greet("张三", "你好"))    # 输出: 你好, 张三!

# 无意义的Lambda（仅演示语法）
# 等价于: def noop(): pass
noop = lambda: None            # 返回None的Lambda
print(noop())                  # 输出: None

# 带条件表达式的Lambda
# 等价于: def abs_val(x): return x if x >= 0 else -x
abs_val = lambda x: x if x >= 0 else -x  # 计算绝对值
print(abs_val(-10))            # 输出: 10
