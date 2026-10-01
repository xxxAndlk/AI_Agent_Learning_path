# 练习3参考答案：矩形类
# 易错点：方法里要用 self.length / self.width，写成光溜溜的 length 会报未定义

class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width

    def perimeter(self):
        return (self.length + self.width) * 2


r1 = Rectangle(4, 3)
r2 = Rectangle(5.5, 2)   # 长宽带小数也一样能用

print("矩形1：面积", r1.area(), "周长", r1.perimeter())
print("矩形2：面积", r2.area(), "周长", r2.perimeter())
