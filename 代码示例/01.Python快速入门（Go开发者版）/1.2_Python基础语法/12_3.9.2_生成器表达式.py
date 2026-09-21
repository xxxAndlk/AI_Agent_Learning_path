# ============ 生成器表达式（对比Go） ============
# Go: 没有直接对应，需要用channel
# Python:

# 列表推导式（立即计算，占用内存）
squares_list = [x*x for x in range(5)]
print(squares_list)  # [0, 1, 4, 9, 16]

# 生成器表达式（惰性计算，按需生成）
squares_gen = (x*x for x in range(5))
print(squares_gen)   # <generator object <genexpr> at 0x...>

# 迭代时按需计算
for sq in squares_gen:
    print(sq)  # 0, 1, 4, 9, 16

# ============ 生成器 vs 列表的内存对比 ============
import sys

# 列表：一次性占用内存
large_list = [x for x in range(1000000)]
print(sys.getsizeof(large_list))  # 约8MB

# 生成器：仅占用生成器对象本身
large_gen = (x for x in range(1000000))
print(sys.getsizeof(large_gen))   # 约200字节

# ============ 生成器表达式作为函数参数 ============
# 不需要额外圆括号
sum(x*x for x in range(10))           # 285
max(x for x in range(10) if x % 2 == 0)  # 8

# ============ 与列表推导式对比 ============
# 列表推导式：适合小数据集，需要多次迭代
data = [1, 2, 3, 4, 5]
squared_list = [x**2 for x in data]

# 生成器表达式：适合大数据集或无限序列
squared_gen = (x**2 for x in data)

# 两者都支持if过滤
evens_list = [x for x in range(10) if x % 2 == 0]
evens_gen = (x for x in range(10) if x % 2 == 0)
