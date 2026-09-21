# ==================== 与Go的详细对比 ====================

"""
Go的取消机制:
- context.Context 是显式传递的
- 通过 ctx.Done() 通道接收取消信号
- 通过 ctx.Err() 获取取消原因

Python的取消机制:
- asyncio.Cancellation 是协作式的
- 通过 task.cancel() 发送取消请求
- 任务代码需要显式检查并响应取消

关键差异:
1. Go的context是值传递，Python的取消是任务级别的
2. Go需要主动检查ctx.Done()，Python需要在await点检查CancelledError
3. Go的超时是context级别的，Python可以针对单个操作设置
"""

# Go代码示例（对比）:
"""
func withTimeout(ctx context.Context, timeout time.Duration) (context.Context, context.CancelFunc) {
    return context.WithTimeout(ctx, timeout)
}

func doTask(ctx context.Context) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-time.After(2 * time.Second):
        // 执行任务
    }
    return nil
}
"""

# Python代码等效:
"""
async def do_task_with_timeout():
    try:
        async with asyncio.timeout(2):
            await do_task()
    except asyncio.TimeoutError:
        # 处理超时
        pass
"""
