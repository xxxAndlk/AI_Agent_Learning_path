# ==================== 6.5.5 超时传播和嵌套超时 ====================

async def inner_task():
    """内部任务"""
    print("内部任务开始")
    await asyncio.sleep(5)
    print("内部任务完成")
    return "内部结果"

async def outer_task():
    """外部任务，调用内部任务"""
    print("外部任务开始")
    try:
        # 外部超时2秒
        result = await asyncio.wait_for(inner_task(), timeout=2)
        return result
    except asyncio.TimeoutError:
        print("外部任务超时")
        return "超时默认值"

async def nested_timeout_example():
    """嵌套超时示例"""
    # 外层超时
    async with asyncio.timeout(3):
        result = await outer_task()
        print(f"最终结果: {result}")

# 超时传播:
# 当内部wait_for超时时，会抛出TimeoutError
# 外层timeout会捕获这个异常
# 如果不处理，异常会向外传播

# Go对比:
# ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
# result, err := innerFunc(ctx)  // 自动继承超时
