# 1. 使用局部变量（比全局变量快）
# 不推荐
import math

def slow_calc():
    return math.sqrt(100)  # 每次访问全局命名空间

# 推荐
def fast_calc():
    sqrt = math.sqrt  # 缓存到局部变量
    return sqrt(100)

# 2. 使用内置函数
# 不推荐
def sum_manual(numbers):
    total = 0
    for n in numbers:
        total += n
    return total

# 推荐（内置函数用 C 实现）
def sum_fast(numbers):
    return sum(numbers)

# 3. 使用列表推导（比循环快）
# 不推荐
result = []
for i in range(1000):
    result.append(i * 2)

# 推荐
result = [i * 2 for i in range(1000)]

# 4. 使用生成器处理大数据
# 不推荐 - 一次性加载所有数据
def process_all():
    data = list(range(10000000))  # 占用大量内存
    return [x * 2 for x in data]

# 推荐 - 惰性计算
def process_stream():
    for i in range(10000000):
        yield i * 2

# 5. 使用 __slots__ 减少内存开销
class PointWithSlots:
    __slots__ = ['x', 'y']  # 禁用 __dict__，节省内存
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointNormal:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# PointWithSlots 比 PointNormal 节省约 40% 内存
