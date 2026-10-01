# 练习3参考答案：排序取前三

nums = [72, 95, 88, 60, 83, 91, 78]

# 用 sorted()：原列表保持原样，排好的结果作为新列表拿来切片
# reverse=True 是降序；[:3] 取前三个
top3 = sorted(nums, reverse=True)[:3]

print("前三名：")
for score in top3:
    print(f"- {score}")
