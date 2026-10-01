# 1. 先测量，再优化
# 不要过早优化，先找到瓶颈

# 2. 使用合适的数据结构
# list: 动态数组，适合append/pop
# deque: 双端队列，适合两端操作
# set: 哈希集合，适合 membership 测试
# dict: 哈希表，适合 key-value 查找

# 3. 避免全局变量
# 局部变量访问比全局变量快

# 4. 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_func(n):
    """带缓存的函数"""
    # 复杂的计算
    return sum(i * i for i in range(n))

# 5. 使用 multiprocessing 绕过 GIL
from multiprocessing import Pool

def process_item(item):
    return item * 2

if __name__ == '__main__':
    with Pool(4) as pool:
        results = pool.map(process_item, range(10000))
