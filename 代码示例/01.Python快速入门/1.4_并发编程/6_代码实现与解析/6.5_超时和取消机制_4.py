# ==================== 6.5.4 处理 CancelledError ====================

async def task_with_cleanup():
    """正确处理取消的示例"""
    try:
        await asyncio.sleep(10)
        return "成功"
    except asyncio.CancelledError:
        # 重要: 必须重新抛出或处理
        print("执行清理操作...")
        # 可以在这里做一些清理工作
        # 重新抛出以通知调用者
        raise

async def handling_cancelled_error():
    """捕获和处理CancelledError"""
    task = asyncio.create_task(task_with_cleanup())
    
    await asyncio.sleep(1)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("已确认任务取消")

# 注意事项:
# 1. 不要吞掉CancelledError而不重新抛出
# 2. 可以在except块中执行清理逻辑
# 3. 使用return_exceptions=True可以抑制异常
async def suppressed_cancel():
    task = asyncio.create_task(asyncio.sleep(10))
    await asyncio.sleep(1)
    task.cancel()
    # return_exceptions=True 会捕获CancelledError作为正常返回值
    result = await asyncio.gather(task, return_exceptions=True)
    print(f"结果: {result}")  # [None, CancelledError()]
