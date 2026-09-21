# ============ if语句（对比Go） ============
# Go:
# if age >= 18 {
#     fmt.Println("成年人")
# } else if age >= 12 {
#     fmt.Println("青少年")
# } else {
#     fmt.Println("儿童")
# }

# Python:
age = 20
if age >= 18:
    print("成年人")
elif age >= 12:        # 注意：不是else if，是elif
    print("青少年")
else:
    print("儿童")

# 注意：Python没有括号，用缩进表示代码块
# 注意：条件后面有冒号:

# 三元表达式（类似Go的 ? : ）
# Go: status := ifelse(age >= 18, "成年", "未成年")
# Python:
status = "成年" if age >= 18 else "未成年"

# ============ for循环（对比Go） ============
# Python的for是foreach，没有传统的for(i=0; i<n; i++)

# 遍历列表
# Go: for i, v := range items { ... }
items = ["a", "b", "c"]
for item in items:
    print(item)

# 需要索引时
for i, item in enumerate(items):
    print(f"{i}: {item}")

# 类似Go的for i := 0; i < 5; i++
# Python使用range()
for i in range(5):           # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):        # 1, 2, 3, 4, 5（类似Go的for i:=1; i<6; i++）
    print(i)

for i in range(0, 10, 2):    # 0, 2, 4, 6, 8（步长为2）
    print(i)

# while循环（Go没有while，用for代替）
# Go: for condition { ... }
# Python:
count = 0
while count < 5:
    print(count)
    count += 1

# break和continue（和Go一样）
for num in range(10):
    if num == 3:
        continue    # 跳过当前迭代
    if num == 7:
        break       # 终止循环
    print(num)
