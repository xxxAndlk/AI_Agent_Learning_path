# 02_计算面积.py —— 练习 2 参考答案
# 算面积的活交给函数，主程序只管把结果拿回来用——所以 return 是必须的

def rect_area(width, height):
    return width * height


a = rect_area(3, 5)
b = rect_area(2.5, 4)

print("3 x 5 的矩形面积：", a)
print("2.5 x 4 的矩形面积：", b)
print("两块地加起来：", a + b)
