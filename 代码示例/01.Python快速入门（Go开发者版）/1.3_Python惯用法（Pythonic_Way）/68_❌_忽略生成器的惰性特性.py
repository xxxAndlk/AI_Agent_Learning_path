# 反模式：生成器只能迭代一次
gen = (x*x for x in range(5))
list(gen)  # [0, 1, 4, 9, 16]
list(gen)  # [] 已耗尽！

# 正确做法：需要多次迭代时转换为列表
gen = [x*x for x in range(5)]  # 使用列表推导
# 或
gen = list(x*x for x in range(5))
