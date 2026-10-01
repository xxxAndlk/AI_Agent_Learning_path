# guess_funcs.py —— 猜数字游戏（函数版，第 7 课）
# 运行方法（在终端里）：python guess_funcs.py
# 玩法和第 6 课完全一样：猜一个 1 到 100 的数，程序提示大了还是小了。
# 区别在于：这次整个游戏被拆成了三个函数，每个只管一件事。

import random


def make_answer():
    # 只负责出题：从 1 到 100 里随机取一个整数
    return random.randint(1, 100)


def check_guess(guess, answer):
    # 只负责判断一次猜测，把结果递出去；不输入、不循环、不打印
    # 返回的这串提示马上会在 main 里派上用场——这就是 return 的意义
    if guess < answer:
        return "小了，往大猜"
    if guess > answer:
        return "大了，往小猜"
    return "对了"


def main():
    # 主流程：出题 -> 反复问玩家 -> 判断 -> 计数，游戏的大纲一眼就能看明白
    answer = make_answer()
    times = 0  # 猜了几次

    print("我想好了一个 1 到 100 的数，猜猜看！")
    while True:
        text = input("你猜是几？")
        guess = int(text)  # 只认整数。要是有人乱输字母，程序会当场翻脸——怎么接住它，第 8 课见
        times = times + 1

        result = check_guess(guess, answer)
        print(result)

        if result == "对了":
            print("共猜了 " + str(times) + " 次，收工！")
            break


# 函数必须先定义后调用：上面三份"菜谱"都写好了，最后这一行才正式开演
main()
