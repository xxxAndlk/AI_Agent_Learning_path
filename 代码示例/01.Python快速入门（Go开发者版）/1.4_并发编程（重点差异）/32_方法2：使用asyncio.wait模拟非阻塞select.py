"""
模拟Go的select with default（非阻塞）
"""
import asyncio
from asyncio import Queue

async def non_blocking_receive(queue):
    """非阻塞接收，类似于Go的select with default"""
    # 使用wait_for with timeout=0实现非阻塞
    try:
        # timeout=0 立即超时，如果没有数据则抛异常
        result = await asyncio.wait_for(queue.get(), timeout=0)
        return result
    except asyncio.TimeoutError:
        return None  # 没有数据，非阻塞返回

async def main():
    queue = Queue()
    
    # 尝试非阻塞获取
    print("尝试非阻塞获取...")
    result = await non_blocking_receive(queue)
    print(f"结果: {result}")  # None
    
    # 放入数据后再尝试
    await queue.put("hello")
    result = await non_blocking_receive(queue)
    print(f"结果: {result}")  # "hello"

asyncio.run(main())
