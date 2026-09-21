import itertools

# 基本用法：连续相同元素的分组
data = [1, 1, 1, 2, 2, 3, 3, 3, 3, 1]

# 按值分组
for key, group in itertools.groupby(data):
    print(f"键: {key}, 元素: {list(group)}")
# 输出:
# 键: 1, 元素: [1, 1, 1]
# 键: 2, 元素: [2, 2]
# 键: 3, 元素: [3, 3, 3, 3]
# 键: 1, 元素: [1]

# 重要：groupby只分组连续的相同元素！
# 如果需要全局分组，先排序
unsorted = [3, 1, 2, 1, 2, 3, 1]
sorted_data = sorted(unsorted)
for key, group in itertools.groupby(sorted_data):
    print(f"键: {key}, 元素: {list(group)}")
# 输出:
# 键: 1, 元素: [1, 1, 1]
# 键: 2, 元素: [2, 2]
# 键: 3, 元素: [3, 3]
