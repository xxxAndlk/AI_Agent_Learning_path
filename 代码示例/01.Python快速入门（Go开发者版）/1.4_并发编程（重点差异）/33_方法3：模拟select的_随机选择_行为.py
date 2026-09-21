"""
模拟Go select的随机选择行为
"""
import asyncio
import random
from asyncio import Queue

async def simulate_select_random():
    """模拟Go的select随机选择行为"""
    queue1 = Queue()
    queue2 = Queue()
    queue3 = Queue()
    
    # 几乎同时放入数据（模拟多个Channel同时就绪）
    await queue1.put("A")
    await queue2.put("B")
    await queue3.put("C")
    
    # 创建获取任务
    queues = [queue1, queue2, queue3]
    
    # 方法1：手动随机选择（类似Go的行为）
    # Go: 当多个case同时就绪时，随机选择一个
    available = [q for q in queues if not q.empty()]
    if available:
        chosen = random.choice(available)
        result = await chosen.get()
        print(f"随机选择了: {result}")
    
    # 方法2：使用as_completed但只取第一个
    get_tasks = [asyncio.create_task(q.get()) for q in queues]
    done, pending = await asyncio.wait(
        get_tasks, 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # 获取第一个完成的结果
    for task in done:
        result = task.result()
        print(f"第一个完成: {result}")
        
    # 取消其他未完成的任务
    for task in pending:
        task.cancel()

asyncio.run(simulate_select_random())
