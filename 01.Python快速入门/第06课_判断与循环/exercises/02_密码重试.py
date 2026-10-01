# 练习 2：密码重试（必做）
# 要点：while 控制最多试 3 次；猜中了用 break 提前跳出，别把机会耗完。
# ok 是一个布尔变量，负责记住"到底猜中没有"——循环结束后还要用它。

password = "py2026"  # 预设的密码，你可以改成自己喜欢的
tries = 0            # 已经试了几次
ok = False           # 先假定没猜中

while tries < 3:
    tries += 1
    guess = input(f"请输入密码（第 {tries} 次，共 3 次机会）：")
    if guess == password:
        ok = True
        print("密码正确，欢迎回来！")
        break
    print("密码不对，再想想。")

if not ok:
    print("三次都没猜中，账号暂时锁定，明天再来吧。")
