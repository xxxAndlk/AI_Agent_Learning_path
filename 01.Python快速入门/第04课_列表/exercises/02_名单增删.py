# 练习2参考答案：名单增删

students = ["小明", "小红", "小刚", "小丽"]

students.insert(1, "小华")   # 插到索引 1，也就是"小红"前面，后面的人自动后移
students.remove("小刚")      # 按"值"删，去掉第一个"小刚"

for name in students:
    print("- " + name)

print(f"现在一共 {len(students)} 个人")
