"""
Python asyncio超时和取消机制 - 对比Go的context.Context
"""
import asyncio
import time

# ==================== 6.5.1 asyncio.wait_for() 设置超时 ====================

async def long_running_task():
    """模拟长时间运行的任务"""
    print("任务开始执行...")
    await asyncio.sleep(5)  # 模拟耗时操作
    print("任务完成!")
    return "任务结果"

async def wait_for_example():
    """wait_for示例：给任务设置超时"""
    try:
        # wait_for(协程, timeout) - 超时抛出asyncio.TimeoutError
        result = await asyncio.wait_for(long_running_task(), timeout=2)
        print(f"结果: {result}")
    except asyncio.TimeoutError:
        print("任务超时被取消!")

# Go对比:
# ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
# result, err := doTask(ctx)

# 运行示例
# asyncio.run(wait_for_example())
