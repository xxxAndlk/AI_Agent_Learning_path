# 练习 3 参考答案：念名单
# 文件不在是常事（第一次运行、手滑改了名），用 try 接住它，别让程序崩。

try:
    with open("names.txt", "r", encoding="utf-8") as f:
        names = f.readlines()        # 一次读进来，一行占一个元素
    greetings = []
    for name in names:
        name = name.strip()          # 脱掉每行末尾看不见的换行符
        if name != "":               # 空行跳过
            greetings.append("你好，" + name)
    for g in greetings:
        print(g)
except FileNotFoundError:
    print("没找到 names.txt：先在程序同一个文件夹里建一个，一行写一个名字。")
