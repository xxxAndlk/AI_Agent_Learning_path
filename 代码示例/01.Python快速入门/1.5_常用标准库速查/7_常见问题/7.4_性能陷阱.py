# 陷阱1: 频繁字符串拼接
result = ""
for i in range(10000):
    result += str(i)  # 慢！每次创建新字符串

# 解决: 使用join
result = "".join(str(i) for i in range(10000))

# 陷阱2: 列表推导vs循环
# 推荐: 列表推导更快
squares = [x**2 for x in range(1000)]  # 快

squares = []
for x in range(1000):  # 稍慢
    squares.append(x**2)
