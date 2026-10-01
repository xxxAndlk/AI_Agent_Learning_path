# 10. 使用any/all代替循环判断
# 不推荐
# has_negative = False
# for x in numbers:
#     if x < 0:
#         has_negative = True
#         break

# 推荐（Pythonic）
numbers = [1, 2, -3, 4, 5]
has_negative = any(x < 0 for x in numbers)
all_positive = all(x > 0 for x in numbers)
