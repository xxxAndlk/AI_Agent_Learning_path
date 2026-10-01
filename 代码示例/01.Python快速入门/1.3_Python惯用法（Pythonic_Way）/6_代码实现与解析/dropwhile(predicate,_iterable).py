import itertools

# 基本用法：跳过开头的负数
numbers = [-3, -2, -1, 0, 1, 2, 3, 4, 5]

# 丢弃负数，保留非负数
result = list(itertools.dropwhile(lambda x: x < 0, numbers))
print(result)  # [0, 1, 2, 3, 4, 5]

# 常用场景：跳过文件开头的空行或注释
lines = ['', '', '# comment', 'data1', 'data2', 'data3']
content = list(itertools.dropwhile(lambda x: x == '', lines))
print(content)  # ['# comment', 'data1', 'data2', 'data3']
