"""
Python asyncio示例 - 对比Go的Goroutine + Channel
"""
import asyncio
from asyncio import Queue

# Go: go func() { ... }()
# Python: asyncio.create_task(coro())

async def say_hello():
    """异步函数（类似Go的函数）"""
    print("Hello")
    await asyncio.sleep(1)  # 非阻塞等待
    print("World")

async def task(name, delay):
    """异步任务"""
    print(f"Task {name} started")
    await asyncio.sleep(delay)
    print(f"Task {name} finished")
    return f"Result-{name}"

async def main():
    # 创建任务（类似Go的go关键字）
    task1 = asyncio.create_task(task("A", 2))
    task2 = asyncio.create_task(task("B", 1))
    
    # 等待所有完成（类似Go的wg.Wait()）
    results = await asyncio.gather(task1, task2)
    print(f"Results: {results}")
