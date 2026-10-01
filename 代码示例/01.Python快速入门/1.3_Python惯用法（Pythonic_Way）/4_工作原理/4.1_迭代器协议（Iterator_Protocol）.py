# 迭代器协议核心方法
class MyIterator:
    def __iter__(self):
        return self  # 返回迭代器对象本身
    
    def __next__(self):
        # 返回下一个值，没有更多元素时抛出StopIteration
        if self.index >= len(self.data):
            raise StopIteration
        value = self.data[self.index]
        self.index += 1
        return value
