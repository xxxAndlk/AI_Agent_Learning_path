# ==================== 6.5.6 实际应用场景 ====================

# 场景1: HTTP请求超时
import asyncio
import aiohttp

async def fetch_with_timeout(url, timeout_seconds=5):
    """带超时的HTTP请求"""
    try:
        async with asyncio.timeout(timeout_seconds):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.text()
    except asyncio.TimeoutError:
        print(f"请求 {url} 超时")
        return None
    except aiohttp.ClientError as e:
        print(f"请求错误: {e}")
        return None

# Go对比:
# ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
# resp, err := http.GetWithContext(ctx, url)


# 场景2: 并行任务超时（至少一个成功）
async def try_multiple_services():
    """尝试多个服务，只要一个成功即可"""
    async def service_a():
        await asyncio.sleep(3)
        return "Service A OK"
    
    async def service_b():
        await asyncio.sleep(1)
        return "Service B OK"
    
    async def service_c():
        await asyncio.sleep(2)
        return "Service C OK"
    
    # 创建所有任务
    tasks = [
        asyncio.create_task(service_a()),
        asyncio.create_task(service_b()),
        asyncio.create_task(service_c()),
    ]
    
    # 等待第一个成功，或全部超时
    done, pending = await asyncio.wait(
        tasks,
        timeout=2,
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # 取消未完成的任务
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    # 返回完成任务的结果
    if done:
        return await done.pop()
    return None


# 场景3: 带取消功能的超时限制
class TimeoutTask:
    """带超时和取消的任务封装"""
    
    def __init__(self, coro, timeout=None):
        self.task = asyncio.create_task(coro)
        self.timeout = timeout
        self._cancelled = False
    
    async def wait(self):
        """等待任务完成，支持超时"""
        if self.timeout:
            try:
                return await asyncio.wait_for(self.task, timeout=self.timeout)
            except asyncio.TimeoutError:
                self.task.cancel()
                self._cancelled = True
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
                return None
        return await self.task
    
    def cancel(self):
        """取消任务"""
        if not self.task.done():
            self.task.cancel()
            self._cancelled = True


async def timeout_task_demo():
    """TimeoutTask使用示例"""
    task = TimeoutTask(asyncio.sleep(5), timeout=2)
    result = await task.wait()
    print(f"结果: {result}")  # None，因为超时


# 场景4: 使用shield保护任务不被取消
async def critical_task():
    """关键任务，不应被取消"""
    for i in range(10):
        await asyncio.sleep(0.5)
        print(f"关键任务进度: {i+1}")
    return "关键任务完成"

async def shield_example():
    """shield保护关键任务"""
    task = asyncio.create_task(critical_task())
    
    await asyncio.sleep(1.5)
    
    # 使用shield保护任务不被取消
    # 即使外层取消，shield内的任务仍会继续执行
    try:
        # 注意: shield应该在外层使用，而不是在task内部
        # 这里演示一个正确用法
        result = await asyncio.wait_for(
            shield(critical_task()),  # 保护critical_task不被取消
            timeout=1
        )
    except asyncio.TimeoutError:
        print("shield外的操作超时，但关键任务继续执行")
    
    # 等待关键任务完成
    if not task.done():
        result = await task
        print(f"最终结果: {result}")

# shield函数可以保护一个协程不被外部取消
# Go等价: 使用独立的context，不继承父context的取消信号
