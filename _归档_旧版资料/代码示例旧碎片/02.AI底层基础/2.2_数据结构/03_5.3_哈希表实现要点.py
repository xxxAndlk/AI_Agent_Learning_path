# 好的哈希函数设计原则
def good_hash(key, size):
    # 多项式滚动哈希
    h = 0
    for char in str(key):
        h = (h * 31 + ord(char)) % size
    return h

# 扩容策略
class DynamicHashTable:
    def __init__(self, initial_capacity=16, load_factor=0.75):
        self.capacity = initial_capacity
        self.load_factor = load_factor
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]
    
    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)  # 重新哈希
