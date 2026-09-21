# ==================== 6.5.2 task.cancel() 手动取消任务 ====================

async def cancellable_task(task_id):
    """可取消的任务示例"""
    try:
        print(f"任务 {task_id} 开始")
        for i in range(10):
            # 模拟耗时操作
            await asyncio.sleep(0.5)
            print(f"任务 {task_id} 进度: {i+1}/10")
        return f"任务 {task_id} 完成"
    except asyncio.CancelledError:
        # 清理资源
        print(f"任务 {task_id} 被取消，正在清理...")
        raise  # 重新抛出CancelledError

async def cancel_example():
    """手动取消任务示例"""
    task = asyncio.create_task(cancellable_task("A"))
    
    # 模拟其他操作
    await asyncio.sleep(2)
    
    # 取消任务
    print("请求取消任务...")
    task.cancel()
    
    try:
        await task  # 等待任务取消完成
    except asyncio.CancelledError:
        print("任务已确认取消")

# Go对比:
# ctx, cancel := context.WithCancel(context.Background())
# go doTask(ctx)
# cancel()  // 手动取消
