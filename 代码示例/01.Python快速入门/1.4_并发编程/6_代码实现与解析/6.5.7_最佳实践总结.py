import asyncio

# 最佳实践1: 总是处理CancelledError（模式参考）
async def good_cancellable():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        # 执行清理
        raise  # 重新抛出

async def async_operation():
    await asyncio.sleep(60)

async def operation1():
    await asyncio.sleep(0.1)

async def operation2():
    await asyncio.sleep(0.1)

async def critical_operation():
    await asyncio.sleep(0.2)

async def main():
    # 最佳实践2: 使用wait_for设置单个操作超时
    try:
        result = await asyncio.wait_for(async_operation(), timeout=5)
    except asyncio.TimeoutError:
        print("操作超时，已取消")

    # 最佳实践3: 使用timeout上下文管理多个操作（Python 3.11+）
    async with asyncio.timeout(10):
        await operation1()
        await operation2()

    # 最佳实践4: 使用shield保护关键任务不被误取消
    result = await asyncio.shield(critical_operation())

    # 最佳实践5: 取消时等待确认
    task = asyncio.create_task(asyncio.sleep(60))
    task.cancel()
    try:
        await task  # 等待取消完成
    except asyncio.CancelledError:
        pass  # 确认取消

if __name__ == "__main__":
    asyncio.run(main())
