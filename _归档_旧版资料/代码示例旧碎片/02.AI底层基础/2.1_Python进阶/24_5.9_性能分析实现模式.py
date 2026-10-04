# cProfile性能分析
import cProfile
import pstats
import io

def heavy_function():
    total = 0
    for i in range(100000):
        total += i ** 2
    return total

profiler = cProfile.Profile()
profiler.enable()
heavy_function()
profiler.disable()

# 输出统计信息
stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 前10个函数
print(stream.getvalue())

# timeit精确测量
import timeit

setup = "import numpy as np; a = np.random.rand(1000, 1000)"
code = "np.dot(a, a)"

# 执行100次，取平均值
result = timeit.repeat(code, setup, number=100, repeat=5)
print(f"平均时间: {sum(result)/len(result):.4f}秒")

# line_profiler行级分析（需单独安装：pip install line_profiler）
# 在函数前添加 @profile 装饰器
# 运行：kernprof -l -v script.py
"""
@profile
def slow_function():
    total = 0
    for i in range(10000):
        for j in range(10000):
            total += i * j
    return total
"""

import numpy
