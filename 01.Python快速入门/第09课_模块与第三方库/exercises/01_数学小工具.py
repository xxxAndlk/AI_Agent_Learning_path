# 练习 1 参考答案：用标准库 math 做几个小计算。
# math 是 Python 自带的，不用安装。

import math

# sqrt 是 square root（平方根）的缩写：6 米见方的菜地，对角线多长？
side = 6
print(f"边长 {side} 米的正方形菜地，对角线约 {math.sqrt(side ** 2 + side ** 2):.2f} 米")

# ceil 是 ceiling（天花板）的缩写：向上取整。买地砖不能买半块，有小数一律进一位
print("铺 23.2 平米地面，要买", math.ceil(23.2), "平米的地砖")

# pi 就是圆周率，math 帮你存好了，不用自己敲 3.14159……
print(f"半径 3 米的圆形花坛，面积约 {math.pi * 3 ** 2:.2f} 平米")
