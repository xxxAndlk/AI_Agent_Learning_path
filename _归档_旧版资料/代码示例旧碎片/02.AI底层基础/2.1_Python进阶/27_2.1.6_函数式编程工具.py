from functools import lru_cache, partial, reduce  # 导入functools工具
import itertools                                   # 导入itertools模块

# ============ 1. lru_cache缓存 ============
@lru_cache(maxsize=128)                           # 最多缓存128个不同参数的结果
def fibonacci(n: int) -> int:
    """斐波那契数列计算（带缓存）
    
    使用缓存后，相同参数的计算只执行一次
    后续直接返回缓存结果
    
    参数:
        n: 第n个斐波那契数
    返回:
        斐波那契数值
    """
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# ============ 2. partial偏函数 ============
def power(base: float, exponent: float) -> float:
    """幂运算
    
    参数:
        base: 底数
        exponent: 指数
    返回:
        底数的指数次方
    """
    return base ** exponent

# 创建偏函数：固定某些参数
square = partial(power, exponent=2)               # 平方函数
cube = partial(power, exponent=3)                 # 立方函数
cube_root = partial(power, base=2)                # 2的x次方根

# ============ 3. reduce归约 ============
def multiply(x: float, y: float) -> float:
    """乘法运算"""
    return x * y

numbers = [1, 2, 3, 4, 5]

# 使用reduce计算乘积
product = reduce(multiply, numbers)               # 1*2*3*4*5 = 120
print(f"乘积: {product}")

# 使用lambda
sum_of_squares = reduce(lambda s, x: s + x**2, numbers, 0)
print(f"平方和: {sum_of_squares}")

# ============ 4. itertools常用函数 ============
# count: 无限计数器
print("偶数计数器:")
for i, num in enumerate(itertools.count(0, 2)):  # 从0开始，步长2
    if i >= 5:                                    # 只取前5个
        break
    print(num, end=" ")
print()

# cycle: 无限循环
print("\n循环重复:")
colors = ['红', '绿', '蓝']
cycled = itertools.cycle(colors)
for i, color in enumerate(cycled):
    if i >= 6:                                    # 循环6次
        break
    print(color, end=" ")
print()

# chain: 连接多个迭代器
print("\n链接迭代器:")
combined = itertools.chain([1, 2], [3, 4], [5])
print(list(combined))

# islice: 切片迭代器（不创建中间列表）
print("\n迭代器切片:")
data = range(10)
sliced = itertools.islice(data, 2, 8, 2)         # 从索引2到8，步长2
print(list(sliced))

# groupby: 分组
print("\n分组:")
data = [('猫', '动物'), ('狗', '动物'), ('树', '植物')]
for key, group in itertools.groupby(data, lambda x: x[1]):
    print(f"{key}: {list(group)}")

# ============ 5. map-filter-reduce管道 ============
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 管道：找出偶数的平方，再求和
result = reduce(
    lambda x, y: x + y,                          # 求和
    map(lambda x: x ** 2,                        # 平方
        filter(lambda x: x % 2 == 0, data)       # 过滤偶数
    )
)
print(f"偶数平方和: {result}")

# ============ 6. 函数组合 ============
def compose(*functions):
    """函数组合：将多个函数组合成一个
    
    compose(f, g, h)(x) 等价于 f(g(h(x)))
    """
    def composed(x):
        result = x
        for func in reversed(functions):         # 反向应用
            result = func(result)
        return result
    return composed

# 示例：先加倍，再加1
double = lambda x: x * 2
increment = lambda x: x + 1

process = compose(increment, double)              # 先double再increment
print(f"process(5) = {process(5)}")              # (5 * 2) + 1 = 11

# ============ 主程序入口 ============
if __name__ == "__main__":
    # 测试缓存效果
    import time
    
    # 无缓存版本（实际测试可观察到差异）
    def fib_no_cache(n):
        if n < 2:
            return n
        return fib_no_cache(n-1) + fib_no_cache(n-2)
    
    # 有缓存版本
    @lru_cache(maxsize=100)
    def fib_with_cache(n):
        if n < 2:
            return n
        return fib_with_cache(n-1) + fib_with_cache(n-2)
    
    n = 30
    start = time.time()
    result1 = fib_no_cache(n)
    print(f"无缓存: {result1}, 耗时: {time.time() - start:.4f}秒")
    
    start = time.time()
    result2 = fib_with_cache(n)
    print(f"有缓存: {result2}, 耗时: {time.time() - start:.4f}秒")
    
    # 使用偏函数
    print(f"\nsquare(4) = {square(4)}")            # 16
    print(f"cube(3) = {cube(3)}")                # 27
    print(f"cube_root(8) = {cube_root(8)}")      # 2.0
