"""
asyncio.Event 事件通知示例 - 对比Go的sync.Cond或channel
"""
import asyncio

# Go版本（使用channel模拟）:
# done := make(chan struct{})
# go func() {
#     // 完成工作
#     close(done)  // 发送信号
# }()
# <-done  // 等待信号

# Python版本
async def worker(event: asyncio.Event, worker_id: int):
    """工作协程，完成后设置事件"""
    print(f"Worker-{worker_id} 开始工作")
    await asyncio.sleep(worker_id * 0.5)  # 模拟工作
    print(f"Worker-{worker_id} 完成")
    event.set()  # 设置事件（通知主协程）

async def main():
    # 创建事件对象
    event = asyncio.Event()
    
    # 创建并启动多个工作协程
    tasks = [asyncio.create_task(worker(event, i)) for i in range(3)]
    
    # 等待所有工作完成
    await event.wait()
    print("所有Worker完成！")
    
    # 清理任务
    for task in tasks:
        await task

# 使用Event实现更精细的等待控制
class AsyncBarrier:
    """异步屏障 - 等待所有协程到达某一点"""
    
    def __init__(self, parties: int):
        self.parties = parties
        self.waiting = 0
        self.event = asyncio.Event()
    
    async def wait(self):
        """等待所有协程到达"""
        self.waiting += 1
        
        if self.waiting >= self.parties:
            self.event.set()
        else:
            await self.event.wait()
        
        self.event.clear()
        self.waiting = 0

async def barrier_example():
    """屏障使用示例"""
    barrier = AsyncBarrier(3)
    
    async def phase_worker(phase: int):
        print(f"Phase {phase} 开始")
        await barrier.wait()
        print(f"Phase {phase} 结束")
    
    for phase in range(2):
        tasks = [asyncio.create_task(phase_worker(phase)) for _ in range(3)]
        await asyncio.gather(*tasks)

# 运行
asyncio.run(barrier_example())
