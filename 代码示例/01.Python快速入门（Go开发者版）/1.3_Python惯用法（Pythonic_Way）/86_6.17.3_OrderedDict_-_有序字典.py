# 实际案例：LRU缓存（Python 3.7+也可用普通字典实现，但OrderedDict更直观）
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        if key not in self.cache:
            return -1
        # 访问后移到末尾（表示最近使用）
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # 移除最旧的（最前面的）
            self.cache.popitem(last=False)

cache = LRUCache(3)
cache.put('a', 1)
cache.put('b', 2)
cache.put('c', 3)
cache.get('a')  # 访问a，a移到末尾
cache.put('d', 4)  # 超出容量，移除最旧的b
print(cache.cache)  # OrderedDict([('c', 3), ('a', 1), ('d', 4)])
