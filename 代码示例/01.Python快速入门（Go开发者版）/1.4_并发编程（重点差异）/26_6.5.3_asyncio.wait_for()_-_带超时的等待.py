"""
asyncio.wait_for() 示例 - 带超时的等待
"""
import asyncio

async def fast_task():
    """快速任务（0.5秒完成）"""
    await asyncio.sleep(0.5)
    return "快速任务完成"

async def slow_task():
    """慢速任务（5秒完成）"""
    await asyncio.sleep(5)
    return "慢速任务完成"

async def main():
    # 场景1：快速任务在超时时间内完成
    print("=== 测试1：任务在超时时间内完成 ===")
    try:
        # wait_for(协程, 超时时间)
        # 如果在超时时间内完成，返回结果
        # 如果超时，抛出asyncio.TimeoutError
        result = await asyncio.wait_for(fast_task(), timeout=2.0)
        print(f"结果: {result}")
    except asyncio.TimeoutError:
        print("超时了！")

    # 场景2：任务超时
    print("\n=== 测试2：任务超时 ===")
    try:
        result = await asyncio.wait_for(slow_task(), timeout=1.0)
        print(f"结果: {result}")
    except asyncio.TimeoutError:
        print("超时了！任务被取消")

    # 场景3：取消操作
    print("\n=== 测试3：手动取消任务 ===")
    task = asyncio.create_task(slow_task())
    
    # 等待一段时间后取消
    await asyncio.sleep(0.5)
    task.cancel()  # 取消任务
    
    try:
        await task
    except asyncio.CancelledError:
        print("任务被取消")

asyncio.run(main())
