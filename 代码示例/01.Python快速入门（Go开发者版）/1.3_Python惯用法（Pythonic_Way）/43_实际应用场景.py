import itertools

# 场景1：统计连续相同元素的个数
data = [1, 1, 1, 2, 2, 3, 3, 3, 3]
runs = [(key, len(list(group))) for key, group in itertools.groupby(data)]
print(runs)  # [(1, 3), (2, 2), (3, 4)]

# 场景2：行程长度编码（RLE）
def rle_encode(data):
    """行程长度编码"""
    return [(key, len(list(group))) for key, group in itertools.groupby(data)]

print(rle_encode('AAAABBBCCDAA'))
# [('A', 4), ('B', 3), ('C', 2), ('D', 1), ('A', 2)]
