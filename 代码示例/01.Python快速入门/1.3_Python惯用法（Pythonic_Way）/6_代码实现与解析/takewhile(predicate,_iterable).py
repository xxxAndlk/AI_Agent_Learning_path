import itertools

# 基本用法：只取前缀正数
numbers = [1, 2, 3, -1, 2, 3]
result = list(itertools.takewhile(lambda x: x > 0, numbers))
print(result)  # [1, 2, 3]

# 常用场景：读取文件直到特定分隔符
lines = ['header1', 'header2', '---', 'data1', 'data2']
header = list(itertools.takewhile(lambda x: x != '---', lines))
print(header)  # ['header1', 'header2']
