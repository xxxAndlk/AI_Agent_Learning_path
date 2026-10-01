import itertools

# 基本用法：获取所有2元素组合
letters = ['A', 'B', 'C', 'D']
combo = list(itertools.combinations(letters, 2))
print(combo)
# [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D'), ('C', 'D')]

# 常用场景：生成测试用例的所有子集
def all_subsets(items):
    """生成所有子集"""
    result = []
    for r in range(len(items) + 1):
        result.extend(itertools.combinations(items, r))
    return result

print(all_subsets([1, 2, 3]))
# [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
