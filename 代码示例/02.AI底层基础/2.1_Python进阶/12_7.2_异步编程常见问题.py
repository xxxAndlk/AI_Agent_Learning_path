# 问题代码：在异步函数中使用阻塞操作
async def bad_example():
    time.sleep(5)  # ❌ 阻塞整个事件循环
    return "Done"

# 解决方案：使用异步版本
async def good_example():
    await asyncio.sleep(5)  # ✅ 非阻塞
    return "Done"

# CPU密集型任务应放入线程池
async def cpu_bound():
    loop = asyncio.get_running_loop()  # 替代已弃用的get_event_loop()
    result = await loop.run_in_executor(None, heavy_computation)
    return result
