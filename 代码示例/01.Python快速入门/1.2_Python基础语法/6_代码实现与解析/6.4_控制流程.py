# ============ if语句 ============
# if age >= 18 {
#     fmt.Println("成年人")
# } else if age >= 12 {
#     fmt.Println("青少年")
# } else {
#     fmt.Println("儿童")
# }

# 
age = 20
if age >= 18:
    print("成年人")
elif age >= 12:        # 注意：不是else if，是elif
    print("青少年")
else:
    print("儿童")

# 注意：Python没有括号，用缩进表示代码块
# 注意：条件后面有冒号:

# 三元表达式
# 
status = "成年" if age >= 18 else "未成年"

# ============ for循环 ============
# Python的for是foreach，没有传统的for(i=0; i<n; i++)

# 遍历列表
items = ["a", "b", "c"]
for item in items:
    print(item)

# 需要索引时
for i, item in enumerate(items):
    print(f"{i}: {item}")

# 类似静态语言的for i := 0; i < 5; i++
# Python使用range()
for i in range(5):           # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):        # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):    # 0, 2, 4, 6, 8（步长为2）
    print(i)

# while循环
# 
count = 0
while count < 5:
    print(count)
    count += 1

# break和continue
for num in range(10):
    if num == 3:
        continue    # 跳过当前迭代
    if num == 7:
        break       # 终止循环
    print(num)
