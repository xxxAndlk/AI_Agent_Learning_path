import itertools

# 基本用法：过滤偶数，保留奇数
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
odds = list(itertools.filterfalse(lambda x: x % 2 == 0, numbers))
print(odds)  # [1, 3, 5, 7, 9]

# 常用场景：分离数据
data = [1, 2, 3, 4, 5, 6]
passed = list(itertools.filterfalse(lambda x: x < 3, data))
print(passed)  # [3, 4, 5, 6]
