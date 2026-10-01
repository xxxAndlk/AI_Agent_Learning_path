import itertools

# 组合多个itertools函数
def process_data(data):
    """数据处理管道"""
    # 1. 过滤非负数
    positive = itertools.filterfalse(lambda x: x < 0, data)
    # 2. 平方
    squared = map(lambda x: x * x, positive)
    # 3. 取前10个
    limited = itertools.islice(squared, 10)
    # 4. 与索引配对
    indexed = enumerate(limited)
    # 5. 过滤value > 10的
    filtered = filter(lambda x: x[1] > 10, indexed)
    return list(filtered)

data = [-3, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
result = process_data(data)
print(result)
# [(4, 16), (5, 25), (6, 36), (7, 49), (8, 64), (9, 81)]
