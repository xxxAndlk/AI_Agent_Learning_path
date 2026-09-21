# ============ 无限序列生成（对比Go） ============
# Go: channel可以处理无限数据流
# func fibonacci() chan int {
#     ch := make(chan int)
#     go func() {
#         a, b := 0, 1
#         for {
#             ch <- a
#             a, b = b, a+b
#         }
#     }()
#     return ch
# }

# Python: 生成器天然支持无限序列
def fibonacci():
    """无限斐波那契数列生成器"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 使用
fib = fibonacci()
for i in range(10):
    print(next(fib))  # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

# 无限自然数
def natural_numbers(start=1):
    """生成无限自然数"""
    n = start
    while True:
        yield n
        n += 1

# 无限素数
def primes():
    """生成无限素数序列"""
    yield 2
    n = 3
    while True:
        is_prime = True
        for p in range(3, int(n**0.5) + 1, 2):
            if n % p == 0:
                is_prime = False
                break
        if is_prime:
            yield n
        n += 2

# 组合生成器：无限序列的转换
def take(n, generator):
    """从生成器取前n个元素"""
    for i, item in enumerate(generator):
        if i >= n:
            break
        yield item

# 使用
first_10_fib = take(10, fibonacci())
print(list(first_10_fib))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# 管道操作
def pipeline_example():
    """生成器管道：过滤和转换"""
    # 1到100的平方，过滤偶数
    result = (
        x * x           # 转换
        for x in range(1, 101)  # 生成
        if (x * x) % 2 == 0     # 过滤
    )
    return result

print(list(take(10, pipeline_example())))
# [4, 16, 36, 64, 100, 144, 196, 256, 324, 400]
