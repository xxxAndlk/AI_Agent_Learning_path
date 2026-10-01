# 练习 1 参考答案：推导式热身
# 给一组数：① 平方列表 ② 筛出偶数 ③ "数字: 平方" 字典

nums = [3, 8, 5, 12, 7, 6, 1]

squares = [x * x for x in nums]          # 基础推导式
evens = [x for x in nums if x % 2 == 0]  # 带 if 筛选
square_map = {x: x * x for x in nums}    # 字典推导式：冒号左边是键

print("原数列:", nums)
print("平方列表:", squares)
print("偶数:", evens)
print("数字:平方 字典:", square_map)
