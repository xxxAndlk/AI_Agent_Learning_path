import cProfile                                # 导入性能分析器
import pstats                                  # 导入统计分析模块
import io                                      # 导入IO模块
import timeit                                  # 导入精确计时模块
import time                                     # 导入时间模块
from functools import lru_cache                # 导入缓存装饰器

# ============ 1. cProfile 函数级性能分析 ============
def fibonacci(n: int) -> int:
    """斐波那契数列递归实现（未优化）"""
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def complex_computation(n: int) -> int:
    """复杂计算：包含多种操作

import numpy

    
    参数:
        n: 计算规模
    返回:
        计算结果
    """
    total = 0
    for i in range(n):
        # 嵌套循环
        for j in range(i, n):
            total += i * j
            # 函数调用
            total += fibonacci(min(j, 10))
    return total

def run_profiler():
    """运行性能分析器"""
    profiler = cProfile.Profile()
    
    # 开始分析
    profiler.enable()
    result = complex_computation(100)
    profiler.disable()
    
    # 输出统计结果
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    
    # 按累计时间排序，显示前15个函数
    stats.sort_stats('cumulative')
    stats.print_stats(15)
    
    print(stream.getvalue())
    return result

# ============ 2. timeit 精确计时 ============
def benchmark_timeit():
    """使用timeit进行精确性能测试
    
    timeit适合测量小代码片段的执行时间
    """
    # 测试列表推导 vs 生成器
    setup_list = "numbers = range(10000)"
    code_list = "[x**2 for x in numbers]"      # 列表推导
    
    setup_gen = "numbers = range(10000)"
    code_gen = "sum(x**2 for x in numbers)"    # 生成器
    
    # 测试1000次，取5次重复的最小值
    list_time = timeit.repeat(code_list, setup_list, number=1000, repeat=5)
    gen_time = timeit.repeat(code_gen, setup_gen, number=1000, repeat=5)
    
    print(f"列表推导时间: {min(list_time):.4f}秒 (1000次)")
    print(f"生成器时间:   {min(gen_time):.4f}秒 (1000次)")
    
    # 测试函数调用开销
    setup_call = "def simple_func():\n    return 1 + 1"
    code_call = "simple_func()"
    
    call_time = timeit.repeat(code_call, setup_call, number=100000, repeat=5)
    print(f"函数调用时间: {min(call_time):.4f}秒 (100000次)")
    
    # 测试缓存效果
    setup_cached = """
from functools import lru_cache

@lru_cache(maxsize=128)
def fib_cached(n):
    if n < 2:
        return n
    return fib_cached(n-1) + fib_cached(n-2)

fib_cached(30)
"""
    
    code_uncached = "fib_cached(30)"
    cached_time = timeit.repeat(code_uncached, setup_cached, number=100, repeat=3)
    print(f"缓存后递归: {min(cached_time):.4f}秒 (100次)")

# ============ 3. 手动计时装饰器 ============
class Timer:
    """简单的计时器类"""
    
    def __init__(self, name: str = "操作"):
        self.name = name
        self.start = None
    
    def __enter__(self):
        self.start = time.perf_counter()        # 高精度计时
        return self
    
    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start
        print(f"{self.name} 耗时: {elapsed:.4f}秒")

def manual_timing():
    """手动计时示例"""
    with Timer("列表排序"):
        data = [3, 1, 4, 1, 5, 9, 2, 6]
        sorted_data = sorted(data)
    
    with Timer("大量计算"):
        result = sum(i**2 for i in range(100000))
    
    with Timer("嵌套循环"):
        total = 0
        for i in range(1000):
            for j in range(1000):
                total += i * j

# ============ 4. 内存分析（简单示例） ============
def memory_usage_example():
    """简单的内存使用分析
    
    实际项目中可使用 memory_profiler 库进行更精确的分析
    """
    import sys
    
    # 估算对象内存
    small_list = list(range(100))
    large_list = list(range(100000))
    
    print(f"100个元素的列表大小: {sys.getsizeof(small_list)} 字节")
    print(f"100000个元素的列表大小: {sys.getsizeof(large_list)} 字节")
    
    # 列表推导 vs 生成器内存差异
    list_comp = [x**2 for x in range(10000)]
    gen_expr = (x**2 for x in range(10000))
    
    print(f"列表推导内存: {sys.getsizeof(list_comp)} 字节")
    print(f"生成器对象内存: {sys.getsizeof(gen_expr)} 字节")

# ============ 5. 优化建议生成器 ============
def suggest_optimizations():
    """根据分析结果提供优化建议"""
    suggestions = """
性能优化建议：
─────────────────────────────────────────
1. 函数调用开销
   - 内联简单函数减少调用开销
   - 使用@lru_cache缓存重复计算结果

2. 循环优化
   - 将不变计算移到循环外
   - 使用列表推导式替代显式循环
   - 考虑使用numpy向量化操作

3. 内存优化
   - 大数据使用生成器替代列表
   - 使用__slots__减少对象内存
   - 及时释放不需要的大对象

4. 并发优化
   - IO密集型使用线程池
   - CPU密集型使用进程池
   - 避免GIL限制使用multiprocessing
"""
    print(suggestions)

# ============ 主程序入口 ============
if __name__ == "__main__":
    print("=" * 60)
    print("cProfile 性能分析:")
    print("=" * 60)
    run_profiler()
    
    print("\n" + "=" * 60)
    print("timeit 精确计时:")
    print("=" * 60)
    benchmark_timeit()
    
    print("\n" + "=" * 60)
    print("手动计时:")
    print("=" * 60)
    manual_timing()
    
    print("\n" + "=" * 60)
    print("内存使用分析:")
    print("=" * 60)
    memory_usage_example()
    
    print("\n" + "=" * 60)
    print("优化建议:")
    print("=" * 60)
    suggest_optimizations()
