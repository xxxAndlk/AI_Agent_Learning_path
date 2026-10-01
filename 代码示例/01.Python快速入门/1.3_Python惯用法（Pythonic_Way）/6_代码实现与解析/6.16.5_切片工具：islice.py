import itertools

# 基本用法：类似列表切片
numbers = range(20)

# 取前5个（类似 numbers[:5]）
first_5 = list(itertools.islice(numbers, 5))
print(first_5)  # [0, 1, 2, 3, 4]

# 取第5到10个（类似 numbers[5:10]）
slice_5_10 = list(itertools.islice(numbers, 5, 10))
print(slice_5_10)  # [5, 6, 7, 8, 9]

# 取第5到15个，步长2（类似 numbers[5:15:2]）
slice_step = list(itertools.islice(numbers, 5, 15, 2))
print(slice_step)  # [5, 7, 9, 11, 13]

# stop为None时取到末尾
to_end = list(itertools.islice(numbers, 5, None))
print(to_end)  # [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
