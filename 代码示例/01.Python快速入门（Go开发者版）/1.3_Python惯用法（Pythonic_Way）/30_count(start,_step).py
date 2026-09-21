import itertools

# 创建一个从0开始的计数器
counter = itertools.count(start=0, step=1)

# 获取前5个值
for i in range(5):
    print(next(counter))  # 输出: 0, 1, 2, 3, 4

# 创建步长为2的计数器（生成偶数）
evens = itertools.count(start=0, step=2)
print(next(evens))  # 0
print(next(evens))  # 2
print(next(evens))  # 4

# 常用场景：带索引的迭代（替代enumerate）
data = ['a', 'b', 'c']
for i, item in zip(itertools.count(1), data):
    print(f"{i}: {item}")
# 输出:
# 1: a
# 2: b
# 3: c
