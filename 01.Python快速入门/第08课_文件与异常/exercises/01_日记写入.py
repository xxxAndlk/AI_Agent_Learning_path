# 练习 1 参考答案：往日记本里写三行
# a 模式追加：diary.txt 不存在会自动创建，存在就在末尾接着写；
# 每次运行都在原有日记后面继续添，跑几次日记就厚几分。

with open("diary.txt", "a", encoding="utf-8") as f:
    f.write(input("今天最开心的一件事：") + "\n")   # 行尾自己补 \n，否则三行挤一行
    f.write(input("今天学到的一个东西：") + "\n")
    f.write(input("明天想做的事：") + "\n")

print("已经写进 diary.txt，明天见。")
