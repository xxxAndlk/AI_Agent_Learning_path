"""
asyncio.Queue 异步队列示例 - 对比Go的channel
"""
import asyncio

# 基础生产者和消费者
async def producer(queue: asyncio.Queue, worker_id: int, count: int):
    for i in range(count):
        item = f"worker-{worker_id}-item-{i}"
        await queue.put(item)
        print(f"Producer-{worker_id} put: {item}")
        await asyncio.sleep(0.1)
    
    await queue.put(None)  # 结束信号

async def consumer(queue: asyncio.Queue, consumer_id: int):
    while True:
        item = await queue.get()
        
        if item is None:
            queue.task_done()
            break
        
        print(f"Consumer-{consumer_id} got: {item}")
        await asyncio.sleep(0.2)
        queue.task_done()

async def basic_example():
    queue = asyncio.Queue(maxsize=10)
    
    producer_task = asyncio.create_task(producer(queue, 1, 5))
    consumer_tasks = [asyncio.create_task(consumer(queue, i)) for i in range(2)]
    
    await producer_task
    await asyncio.gather(*consumer_tasks)
    print("基础示例完成！")

asyncio.run(basic_example())

# 优先队列示例
async def priority_example():
    pq = asyncio.PriorityQueue()
    
    await pq.put((3, "低优先级"))
    await pq.put((1, "高优先级"))
    await pq.put((2, "中优先级"))
    
    for _ in range(3):
        priority, item = await pq.get()
        print(f"优先级 {priority}: {item}")

asyncio.run(priority_example())

# 完整工作者系统
class AsyncWorkerSystem:
    def __init__(self, num_workers: int = 3):
        self.queue = asyncio.Queue()
        self.num_workers = num_workers
        self.workers = []
        self.running = False
    
    async def start(self):
        self.running = True
        self.workers = [asyncio.create_task(self._worker(i)) for i in range(self.num_workers)]
    
    async def _worker(self, worker_id: int):
        while self.running:
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                if item is None:
                    break
                print(f"Worker-{worker_id} 处理: {item}")
                await asyncio.sleep(0.1)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
    
    async def submit(self, item):
        await self.queue.put(item)
    
    async def stop(self):
        self.running = False
        for _ in range(self.num_workers):
            await self.queue.put(None)
        await asyncio.gather(*self.workers)

async def worker_system_example():
    system = AsyncWorkerSystem(num_workers=3)
    await system.start()
    for i in range(10):
        await system.submit(f"task-{i}")
    await system.queue.join()
    await system.stop()
    print("系统示例完成！")

asyncio.run(worker_system_example())
