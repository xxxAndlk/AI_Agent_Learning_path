# 生成器表达式
sum_of_squares = sum(x**2 for x in range(1000000))  # 不创建中间列表

# 生成器函数
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
