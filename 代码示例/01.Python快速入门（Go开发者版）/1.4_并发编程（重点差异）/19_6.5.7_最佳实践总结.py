# 最佳实践1: 总是处理CancelledError
async def good_cancellable():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        # 执行清理
        raise  # 重新抛出

# 最佳实践2: 使用wait_for设置单个操作超时
result = await asyncio.wait_for(async_operation(), timeout=5)

# 最佳实践3: 使用timeout上下文管理多个操作（Python 3.11+）
async with asyncio.timeout(10):
    await operation1()
    await operation2()

# 最佳实践4: 使用shield保护关键任务不被误取消
result = await shield(critical_operation())

# 最佳实践5: 取消时等待确认
task.cancel()
try:
    await task  # 等待取消完成
except asyncio.CancelledError:
    pass  # 确认取消
