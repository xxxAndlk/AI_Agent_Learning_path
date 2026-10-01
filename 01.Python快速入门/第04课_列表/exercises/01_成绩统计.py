# 练习1参考答案：成绩统计
# len() 数个数，max()/min() 找最高最低，sum() 求总和——都是现成的

scores = [88, 92, 75, 63, 90, 81, 59, 77]

count = len(scores)
highest = max(scores)
lowest = min(scores)
average = sum(scores) / len(scores)

print(f"共有 {count} 个成绩")
print(f"最高分：{highest}")
print(f"最低分：{lowest}")
print(f"平均分：{average}")
# 平均分带一长串小数是正常的：除法的结果本来就是这样
# 想只要一位小数，可以用 round(average, 1)
