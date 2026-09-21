# 1. cProfile - 简单的性能分析
import cProfile
import pstats

def heavy_function():
    total = 0
    for i in range(1000000):
        total += i
    return total

# 运行性能分析
profiler = cProfile.Profile()
profiler.enable()
result = heavy_function()
profiler.disable()

# 输出统计信息
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')  # 排序方式：cumulative, time, calls
stats.print_stats(20)           # 显示前20个

# 保存到文件供进一步分析
stats.dump_stats('profile.prof')
# 可以用 snakeviz 可视化: pip install snakeviz && snakeviz profile.prof

# 2. timeit - 精确测量代码执行时间
import timeit

# 测量执行时间
result = timeit.timeit(
    '[x**2 for x in range(1000)]',
    number=1000
)
print(f"执行时间: {result:.4f}秒")

# 测量函数执行时间
def test_function():
    return sum(range(10000))

result = timeit.timeit(test_function, number=1000)
print(f"函数执行时间: {result:.4f}秒")

# 3. line_profiler - 行级性能分析
# pip install line_profiler

@profile  # 需要用 profile 装饰器
def slow_function():
    total = 0
    for i in range(10000):
        for j in range(100):
            total += i * j
    return total

# 运行: kernprof -l -v script.py

# 4. memory_profiler - 内存分析
# pip install memory_profiler

@profile
def memory_intensive():
    data = [i ** 2 for i in range(100000)]
    return data

# 运行: python -m memory_profiler script.py
