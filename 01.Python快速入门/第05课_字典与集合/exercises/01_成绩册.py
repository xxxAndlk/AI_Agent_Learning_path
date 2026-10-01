# 练习1参考答案：成绩册
# 名字 → 分数。加成绩、查某人、遍历打印全部

scores = {"小明": 92, "小红": 85}

# 加成绩：键不存在就是加；名字写重了就是覆盖改分
scores["小刚"] = 78
scores["小红"] = 88

# 查某人：get 兜底，没录入的也不会报错
print("小明的分数：", scores.get("小明"))
print("小丽的分数：", scores.get("小丽", "还没录入"))

# 遍历打印整本成绩册
for name, score in scores.items():
    print(f"{name}：{score} 分")
