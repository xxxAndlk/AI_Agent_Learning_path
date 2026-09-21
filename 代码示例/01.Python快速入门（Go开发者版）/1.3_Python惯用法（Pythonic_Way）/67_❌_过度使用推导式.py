# 反模式：复杂嵌套，难以阅读
result = [[x*y for y in range(10)] for x in range(10) if x % 2 == 0]

# 正确做法：保持简洁或使用函数
def create_row(x):
    return [x*y for y in range(10)]

result = [create_row(x) for x in range(10) if x % 2 == 0]
