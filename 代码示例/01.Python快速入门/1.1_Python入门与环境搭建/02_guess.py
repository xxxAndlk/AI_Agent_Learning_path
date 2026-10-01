# -*- coding: utf-8 -*-
"""02_guess.py —— 猜数字：体验变量、输入、分支与循环
运行：python 02_guess.py
"""
import random                       # 标准库：随机数

secret = random.randint(1, 10)      # 生成 1~10 的随机整数，赋值给变量
print("我想了一个 1~10 的数字，猜猜看！")

while True:                         # 无限循环，直到猜中后 break 退出
    text = input("你的猜测：")       # input() 返回字符串
    guess = int(text)               # 字符串转整数；输错会报 ValueError，见课程第 7 节
    if guess == secret:
        print("🎉 猜对了！答案就是", secret)
        break                       # 跳出循环
    elif guess < secret:
        print("小了，再试试")
    else:
        print("大了，再试试")

print("游戏结束，欢迎进入 1.2 的语法学习！")
