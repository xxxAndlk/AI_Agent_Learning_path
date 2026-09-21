# ============ 迭代器协议（对比Go） ============
# Go: for range自动处理迭代
# Python: 需要实现__iter__和__next__

class Countdown:
    """倒计时迭代器 - 展示迭代器协议"""
    
    def __init__(self, start):
        """初始化迭代器"""
        self.current = start  # 当前计数
        self.start = start    # 起始值（用于重置）
    
    def __iter__(self):
        """返回迭代器本身"""
        return self
    
    def __next__(self):
        """返回下一个值"""
        if self.current <= 0:
            raise StopIteration  # 迭代结束
        self.current -= 1
        return self.current + 1

# 使用迭代器
countdown = Countdown(5)
for num in countdown:
    print(num)  # 5, 4, 3, 2, 1

# ============ 可迭代对象（实现__iter__返回新迭代器） ============
class CountdownRange:
    """可迭代对象 - 可多次迭代"""
    
    def __init__(self, start):
        self.start = start
    
    def __iter__(self):
        """每次调用返回新的迭代器"""
        return Countdown(self.start)

# 可以多次迭代
countdowns = CountdownRange(3)
for num in countdowns:
    print(num)  # 3, 2, 1

for num in countdowns:  # 重新开始
    print(num)  # 3, 2, 1

# ============ 使用iter()函数自定义行为 ============
def custom_iter():
    """展示iter()函数的第二个参数"""
    data = [1, 2, 3, 4, 5]
    for item in data:
        yield item

# iter(callable, sentinel) - 调用直到返回sentinel
def read_lines():
    """模拟读取行，到空行停止"""
    lines = ["第一行", "第二行", "", "忽略此行"]
    for line in lines:
        yield line

# 使用sentinel终止
reader = iter(read_lines().send, "")  # 需要正确实现
# 或者使用iterwith sentinel：
def fibonacci(max_val):
    """生成斐波那契数列直到超过最大值"""
    a, b = 0, 1
    while a < max_val:
        yield a
        a, b = b, a + b

# ============ 迭代器工具（itertools） ============
from itertools import count, cycle, repeat, islice, chain

# count(start, step) - 无限计数器
counter = count(10, 2)  # 10, 12, 14, 16, ...
for i in islice(counter, 5):
    print(i)  # 取前5个

# cycle(iterable) - 循环重复
cycler = cycle([1, 2, 3])  # 1, 2, 3, 1, 2, 3, ...
for i in islice(cycler, 7):
    print(i)

# repeat(elem, n) - 重复元素
repeater = repeat("hello", 3)  # hello, hello, hello

# chain(*iterables) - 链接多个迭代器
chained = chain([1, 2], [3, 4], [5])
print(list(chained))  # [1, 2, 3, 4, 5]
