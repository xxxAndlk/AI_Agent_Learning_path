from functools import reduce, partial, lru_cache
from operator import add, mul

# reduce替代循环累加
total = reduce(add, range(1, 101))  # 5050

# partial创建偏函数
double = partial(mul, 2)
print(double(5))  # 10

# lru_cache缓存函数结果
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))  # 极快，结果被缓存
