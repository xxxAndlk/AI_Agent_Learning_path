# 场景1：调试异步代码
import asyncio

async def debug_async():
    """调试异步代码"""
    import pdb; pdb.set_trace()  # 在异步中仍然可以使用 pdb
    
    task = asyncio.create_task(some_async_func())
    result = await task
    return result

# 场景2：调试类型错误
# 使用 pyright 或 mypy 提前发现类型问题
"""
pip install pyright
pyright your_file.py  # 快速类型检查
"""

# 场景3：调试性能问题
# 使用 cProfile
import cProfile
import pstats

def slow_function():
    # 需要调试的函数
    data = list(range(10000))
    return [x * 2 for x in data]

profiler = cProfile.Profile()
profiler.enable()

result = slow_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 显示前10个最慢的调用
