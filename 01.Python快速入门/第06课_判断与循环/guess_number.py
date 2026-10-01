# 猜数字游戏——第 06 课完全体
# 玩法：程序随机藏一个 1 到 100 的数，你来猜，它只告诉你"大了"还是"小了"。
# 已知不足：输入字母会直接报错退出。先别急，第 08 课学完异常处理，我们回来把它补结实。

import random

answer = random.randint(1, 100)  # 注意：randint 两头都包含，跟 range 的脾气不一样
count = 0                        # 计数变量：记录你猜了几次

print("我藏好了一个 1 到 100 之间的数，看看你几次能猜中！")

while True:
    guess = int(input("你猜是几？"))
    count += 1

    if guess > answer:
        print("大了，往小猜。")
    elif guess < answer:
        print("小了，往大猜。")
    else:
        print(f"猜对了！就是 {answer}，你一共猜了 {count} 次。")
        break  # 已经赢了，跳出循环，游戏结束
