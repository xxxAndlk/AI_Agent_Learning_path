# Python 3.12+ 提供了更清晰的错误追溯
# - 错误位置用箭头精确指向问题行
# - 相关的代码片段高亮显示
# - 简化了复杂追溯的显示

def nested_call():
    return int("not a number")  # 错误会清晰显示在这里

def wrapper():
    return nested_call()  # 追溯会显示调用链

wrapper()
# 新的追溯格式更易读，类似 Go 的错误追溯
