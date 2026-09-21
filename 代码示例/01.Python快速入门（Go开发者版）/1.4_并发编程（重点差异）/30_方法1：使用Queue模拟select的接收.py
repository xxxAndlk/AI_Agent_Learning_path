"""
模拟Go的select接收多个Channel
"""
import asyncio
from asyncio import Queue

async def producer(queue, name, delay):
    """生产者：向队列发送数据"""
    await asyncio.sleep(delay)
    await queue.put(f"{name}的数据")
    print(f"Producer {name}: 发送数据")

async def select_receive_example():
    """模拟 Go select { case <-ch: ... }"""
    # 创建多个队列（相当于多个Channel）
    queue1 = Queue()
    queue2 = Queue()
    queue3 = Queue()
    
    # 创建生产者（模拟Go的go producer()）
    asyncio.create_task(producer(queue1, "A", 1))
    asyncio.create_task(producer(queue2, "B", 2))
    asyncio.create_task(producer(queue3, "C", 0.5))  # 最快
    
    # 收集所有队列
    queues = [queue1, queue2, queue3]
    results = []
    
    # 方法：使用wait和gather结合
    # 等待所有队列有数据
    async def get_one(queue):
        return await queue.get()
    
    # 同时等待所有队列的get操作
    # 但这需要预先知道每个队列都有数据
    
    # 更好的方法：使用as_completed思想
    print("等待数据到达...")
    
    # 创建获取任务
    get_tasks = [asyncio.create_task(q.get()) for q in queues]
    
    # 谁先完成先处理
    for coro in asyncio.as_completed(get_tasks):
        result = await coro
        results.append(result)
        print(f"收到: {result}")
    
    return results

asyncio.run(select_receive_example())
