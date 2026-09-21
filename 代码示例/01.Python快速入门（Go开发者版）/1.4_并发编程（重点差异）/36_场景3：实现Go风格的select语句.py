"""
完整示例：实现Go风格的select语句
"""
import asyncio
from asyncio import Queue
from typing import Any, Optional
import random

class Select:
    """
    模拟Go的select语句
    支持：case接收、case发送、default、timeout
    """
    
    def __init__(self):
        self.cases = []
    
    def case_receive(self, queue: Queue):
        """case <-ch: 接收"""
        self.cases.append(('receive', queue))
        return self
    
    def case_send(self, queue: Queue, value: Any):
        """case ch <- value: 发送"""
        self.cases.append(('send', (queue, value)))
        return self
    
    def case_default(self, func):
        """default: 默认处理"""
        self.cases.append(('default', func))
        return self
    
    async def wait(self, timeout: Optional[float] = None):
        """
        等待并执行第一个就绪的case
        类似于Go的select行为
        """
        if not self.cases:
            return None
        
        # 收集所有可能的等待任务
        tasks = []
        
        for case in self.cases:
            if case[0] == 'receive':
                queue = case[1]
                # 创建一个带超时的get任务
                if timeout:
                    task = asyncio.create_task(
                        asyncio.wait_for(queue.get(), timeout=timeout)
                    )
                else:
                    task = asyncio.create_task(queue.get())
                tasks.append(('receive', task, queue))
            
            elif case[0] == 'send':
                queue, value = case[1]
                task = asyncio.create_task(queue.put(value))
                tasks.append(('send', task, queue, value))
            
            elif case[0] == 'default':
                # 立即执行default
                return case[1]()
        
        if not tasks:
            return None
        
        # 等待任一任务完成（类似select的随机选择）
        done, pending = await asyncio.wait(
            [t[1] for t in tasks],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 处理完成的任务
        for task in pending:
            task.cancel()
        
        completed = list(done)[0]
        
        # 找到对应的case
        for t in tasks:
            if t[1] == completed:
                if t[0] == 'receive':
                    return await completed
                elif t[0] == 'send':
                    return None
        
        return None


# 使用示例
async def go_style_select_demo():
    """Go风格select的使用示例"""
    queue1 = Queue()
    queue2 = Queue()
    
    # 模拟生产者：随机向某个队列发送数据
    async def producer():
        await asyncio.sleep(random.uniform(0.1, 0.5))
        if random.random() > 0.5:
            await queue1.put("来自队列1")
        else:
            await queue2.put("来自队列2")
    
    # 启动生产者
    asyncio.create_task(producer())
    
    # 使用自定义Select（模拟Go的select）
    select = Select()
    result = (
        select
        .case_receive(queue1)
        .case_receive(queue2)
    )
    
    # 等待任意一个队列有数据
    msg = await select.wait(timeout=2.0)
    print(f"收到消息: {msg}")

# 运行
print("=== Go风格Select演示 ===")
asyncio.run(go_style_select_demo())
