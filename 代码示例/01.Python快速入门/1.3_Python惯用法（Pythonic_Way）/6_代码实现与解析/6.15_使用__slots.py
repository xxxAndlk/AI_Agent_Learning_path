# 15. 使用__slots__节省内存
class Point:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
