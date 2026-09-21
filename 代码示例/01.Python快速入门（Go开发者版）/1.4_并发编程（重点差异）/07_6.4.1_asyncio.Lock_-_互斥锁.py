"""
asyncio.Lock 互斥锁示例 - 对比Go的sync.Mutex
"""
import asyncio

# Go版本:
# var mu sync.Mutex
# func criticalSection() {
#     mu.Lock()
#     defer mu.Unlock()
#     // 临界区代码
# }

# Python版本
class AsyncCounter:
    """线程安全的异步计数器"""
    
    def __init__(self):
        self.count = 0
        self.lock = asyncio.Lock()  # 创建锁
    
    async def increment(self):
        """递增计数器（保护共享变量）"""
        async with self.lock:  # 获取锁，自动释放
            self.count += 1
            # 模拟异步IO操作
            await asyncio.sleep(0.01)
            return self.count
    
    async def increment_many(self, n):
        """多次递增"""
        tasks = [self.increment() for _ in range(n)]
        results = await asyncio.gather(*tasks)
        return results

async def main():
    counter = AsyncCounter()
    
    # 启动10个并发任务
    results = await counter.increment_many(10)
    print(f"最终计数: {counter.count}")  # 输出: 10
    print(f"返回结果: {results}")

# 运行示例
asyncio.run(main())
