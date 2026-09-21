"""
实际场景：超时控制与优雅取消
"""
import asyncio

async def critical_operation(name, duration):
    """关键操作，有超时要求"""
    print(f"{name}: 开始执行")
    await asyncio.sleep(duration)
    print(f"{name}: 执行完成")
    return f"{name}成功"

async def main_with_timeout():
    """带超时的主流程"""
    # 创建任务
    task1 = asyncio.create_task(critical_operation("任务1", 2))
    task2 = asyncio.create_task(critical_operation("任务2", 5))
    task3 = asyncio.create_task(critical_operation("任务3", 1))
    
    done, pending = await asyncio.wait(
        [task1, task2, task3],
        timeout=3,  # 3秒超时
        return_when=asyncio.ALL_COMPLETED
    )
    
    print(f"\n=== 超时检查 ===")
    print(f"完成: {len(done)}, 待完成: {len(pending)}")
    
    # 处理完成的任务
    for task in done:
        try:
            result = task.result()
            print(f"✓ {result}")
        except Exception as e:
            print(f"✗ 错误: {e}")
    
    # 处理超时任务
    for task in pending:
        print(f"✗ 任务超时，取消: {task}")
        task.cancel()
    
    # 等待取消完成
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)

asyncio.run(main_with_timeout())
