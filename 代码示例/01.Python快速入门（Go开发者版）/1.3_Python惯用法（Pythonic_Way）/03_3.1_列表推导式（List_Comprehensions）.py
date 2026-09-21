# 基本形式
squares = [x**2 for x in range(10)]

# 带条件过滤
evens = [x for x in range(20) if x % 2 == 0]

# 嵌套推导
matrix = [[i*j for j in range(5)] for i in range(5)]
