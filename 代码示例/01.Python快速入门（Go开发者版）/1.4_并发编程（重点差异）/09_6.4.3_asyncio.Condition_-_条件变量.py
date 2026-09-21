"""
asyncio.Condition 条件变量示例 - 对比Go的sync.Cond
"""
import asyncio

# Python版本
class AsyncBoundedBuffer:
    """有界异步缓冲区（生产者-消费者模式）"""
    
    def __init__(self, max_size: int = 10):
        self.buffer = []
        self.max_size = max_size
        self.condition = asyncio.Condition()
    
    async def put(self, item):
        """放入数据（如果缓冲区满则等待）"""
        async with self.condition:
            while len(self.buffer) >= self.max_size:
                await self.condition.wait()
            
            self.buffer.append(item)
            print(f"Put: {item}, buffer size: {len(self.buffer)}")
            self.condition.notify()
    
    async def get(self):
        """取出数据（如果缓冲区空则等待）"""
        async with self.condition:
            while len(self.buffer) == 0:
                await self.condition.wait()
            
            item = self.buffer.pop(0)
            print(f"Got: {item}, buffer size: {len(self.buffer)}")
            self.condition.notify()
            return item

async def producer(buffer: AsyncBoundedBuffer, count: int):
    """生产者协程"""
    for i in range(count):
        await buffer.put(i)
        await asyncio.sleep(0.1)

async def consumer(buffer: AsyncBoundedBuffer, count: int):
    """消费者协程"""
    for _ in range(count):
        item = await buffer.get()
        await asyncio.sleep(0.15)

async def main():
    buffer = AsyncBoundedBuffer(max_size=5)
    
    producer_task = asyncio.create_task(producer(buffer, 10))
    consumer_task = asyncio.create_task(consumer(buffer, 10))
    
    await asyncio.gather(producer_task, consumer_task)
    print("完成！")

asyncio.run(main())
