import itertools

# 按字符串长度分组
words2 = ['a', 'ab', 'abc', 'abcd', 'xyz', 'xy']
sorted_by_len = sorted(words2, key=len)
for length, group in itertools.groupby(sorted_by_len, key=len):
    print(f"长度 {length}: {list(group)}")
# 输出:
# 长度 1: ['a']
# 长度 2: ['ab', 'xy']
# 长度 3: ['abc', 'xyz']
# 长度 4: ['abcd']
