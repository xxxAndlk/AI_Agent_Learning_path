# Python 3.12 之前：f-string 内不能使用表达式
# Python 3.12+：现在可以嵌套 f-string

name = "Alice"
age = 30

# 嵌套 f-string（3.12+ 新特性）
message = f"Hello, {f'{name.upper()}'}! You are {f'{age} years old'}."
# 输出: Hello, ALICE! You are 30 years old.

# 更复杂的嵌套示例
items = ["apple", "banana", "cherry"]
for i, item in enumerate(items, 1):
    # 嵌套格式化
    print(f"{i}: {item.upper()}")
    # 输出: 1: APPLE

# f-string 内使用调试表达式（3.8+已有，3.12改进）
x = 10
y = 20
print(f"{x + y = }")  # 输出: x + y = 30

# self-documenting 表达式（3.12+）
# 在 f-string 中直接显示变量名和值
name = "Bob"
age = 25
print(f"{name=}, {age=}")
# 输出: name='Bob', age=25
