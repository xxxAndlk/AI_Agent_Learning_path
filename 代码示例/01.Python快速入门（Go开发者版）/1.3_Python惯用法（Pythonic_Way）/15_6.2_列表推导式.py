# 2. 遍历并收集结果（使用列表推导）
# 不推荐：
# result = []
# for x in items:
#     if x > 0:
#         result.append(x * 2)

# 推荐（Pythonic）：
items = [1, -2, 3, -4, 5]
result = [x * 2 for x in items if x > 0]
