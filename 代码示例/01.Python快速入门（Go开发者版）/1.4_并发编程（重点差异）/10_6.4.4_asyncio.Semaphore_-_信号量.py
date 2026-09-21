"""
asyncio.Semaphore 信号量示例 - 对比Go的sync.WaitGroup或channel限流
"""
import asyncio

async def worker(sem: asyncio.Semaphore, worker_id: int):
    """使用信号量限制并发的工作协程"""
    async with sem:
        print(f"Worker-{worker_id} 开始")
        await asyncio.sleep(1)
        print(f"Worker-{worker_id} 结束")

async def main():
    sem = asyncio.Semaphore(3)  # 限制最多3个并发
    
    tasks = [asyncio.create_task(worker(sem, i)) for i in range(10)]
    await asyncio.gather(*tasks)
    print("全部完成！")

asyncio.run(main())

# 实现类似Go的sync.WaitGroup
class AsyncWaitGroup:
    def __init__(self):
        self.count = 0
        self.condition = asyncio.Condition()
    
    def add(self, n: int = 1):
        self.count += n
    
    async def done(self):
        async with self.condition:
            self.count -= 1
            if self.count <= 0:
                self.condition.notify_all()
    
    async def wait(self):
        async with self.condition:
            while self.count > 0:
                await self.condition.wait()

async def wait_group_example():
    wg = AsyncWaitGroup()
    
    async def task_with_wg(task_id: int):
        print(f"Task-{task_id} 开始")
        await asyncio.sleep(task_id * 0.2)
        print(f"Task-{task_id} 结束")
        await wg.done()
    
    wg.add(5)
    for i in range(5):
        asyncio.create_task(task_with_wg(i))
    
    await wg.wait()
    print("所有任务完成！")

asyncio.run(wait_group_example())
