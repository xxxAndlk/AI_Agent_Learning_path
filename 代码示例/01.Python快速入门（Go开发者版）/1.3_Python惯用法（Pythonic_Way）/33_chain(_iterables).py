import itertools

# 基本用法：连接多个序列
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = [7, 8, 9]

chained = itertools.chain(list1, list2, list3)
print(list(chained))  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 常用场景：扁平化嵌套列表（浅层）
nested = [[1, 2], [3, 4], [5, 6]]
flat = list(itertools.chain.from_iterable(nested))
print(flat)  # [1, 2, 3, 4, 5, 6]
