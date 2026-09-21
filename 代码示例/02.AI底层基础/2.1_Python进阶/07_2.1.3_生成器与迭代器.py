class FibonacciIterator:
    """斐波那契数列迭代器类
    
    实现Python迭代器协议：__iter__() 和 __next__()
    可以生成不超过max_num的斐波那契数列
    """
    def __init__(self, max_num: int):
        """初始化迭代器
        
        参数:
            max_num: 斐波那契数列的上限值
        """
        self.max_num = max_num        # 设置最大数值限制
        self.a, self.b = 0, 1         # 斐波那契数列的前两个数：a=当前值, b=下一个值
    
    def __iter__(self):
        """返回迭代器对象自身
        
        这是迭代器协议的要求，使对象可被for循环使用
        """
        return self                   # 返回迭代器实例自身
    
    def __next__(self):
        """返回下一个斐波那契数
        
        当没有更多元素时抛出StopIteration异常
        """
        if self.a > self.max_num:     # 检查是否超过上限
            raise StopIteration       # 超过上限时抛出StopIteration，结束迭代
        current = self.a              # 保存当前值
        self.a, self.b = self.b, self.a + self.b  # 计算下一对斐波那契数
        return current                # 返回当前值

def fibonacci_generator(max_num: int):
    """斐波那契数列生成器函数
    
    使用yield关键字实现，更简洁的迭代器写法
    生成器会在每次yield处暂停，下次从该处继续
    
    参数:
        max_num: 斐波那契数列的上限值
    返回:
        生成器对象，可迭代产生斐波那契数
    """
    a, b = 0, 1                   # 初始化斐波那契数列的前两个数
    while a <= max_num:           # 当当前值不超过上限时继续
        yield a                   # yield产生当前值并暂停，保留函数状态
        a, b = b, a + b           # 更新为下一对斐波那契数

if __name__ == "__main__":
    print("迭代器实现斐波那契:")
    # 使用迭代器类创建实例并遍历
    for num in FibonacciIterator(100):
        print(num, end=" ")       # end=" "使输出在同一行，用空格分隔
    
    print("\n生成器实现斐波那契:")
    # 使用生成器函数，语法更简洁
    for num in fibonacci_generator(100):
        print(num, end=" ")
