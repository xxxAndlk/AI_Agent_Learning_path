import itertools

# 场景：找出和为8的所有两数组合
numbers = [1, 2, 3, 4, 5]
def find_pairs_sum(numbers, target):
    for combo in itertools.combinations(numbers, 2):
        if sum(combo) == target:
            yield combo

print(list(find_pairs_sum(numbers, 8)))  # [(3, 5)]

# 场景：幂集生成（所有子集）
def power_set(items):
    """生成集合的所有子集"""
    return itertools.chain.from_iterable(
        itertools.combinations(items, r) 
        for r in range(len(items) + 1)
    )

items = {1, 2, 3}
subsets = list(power_set(items))
print(subsets)
# [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
