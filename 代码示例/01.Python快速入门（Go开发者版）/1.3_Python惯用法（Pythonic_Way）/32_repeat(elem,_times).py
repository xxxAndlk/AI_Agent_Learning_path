import itertools

# 无限重复
repeat_inf = itertools.repeat('赞')
print(next(repeat_inf))  # 赞
print(next(repeat_inf))  # 赞
# 会一直返回'赞'，永不停止

# 有限次重复（常用场景：与zip配对）
repeated = itertools.repeat('x', 5)
paired = list(zip(range(5), repeated))
print(paired)  # [(0, 'x'), (1, 'x'), (2, 'x'), (3, 'x'), (4, 'x')]

# 常用场景：创建相同元素的列表
five_zeros = list(itertools.repeat(0, 10))
print(five_zeros)  # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# 与map配合使用
squares = list(map(pow, range(5), itertools.repeat(2, 5)))
print(squares)  # [0, 1, 4, 9, 16]  计算0^2, 1^2, 2^2, 3^2, 4^2
