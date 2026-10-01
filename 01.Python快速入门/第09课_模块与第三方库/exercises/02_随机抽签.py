# 练习 2 参考答案：用标准库 random 做抽签。

import random

students = ["小明", "小红", "小刚", "小丽", "小强"]

# choice：从列表里随机拿一个出来，原列表不动
on_duty = random.choice(students)
print("今天值日的是：", on_duty)

# shuffle：洗牌。注意它是直接改原列表，不返回新列表——
# 写 new_list = random.shuffle(students) 只会得到 None，这是新手常错点
random.shuffle(students)
print("抽签顺序：", students)
print("第一个发言的是：", students[0])
