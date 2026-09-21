# ==================== 6.5.3 asyncio.timeout() (Python 3.11+) ====================

async def slow_operation():
    """模拟慢速操作"""
    await asyncio.sleep(10)
    return "完成"

async def timeout_context_example():
    """asyncio.timeout上下文管理器（Python 3.11+推荐）"""
    try:
        # async with timeout(时间): 在块内的所有await都会受超时影响
        async with asyncio.timeout(3):
            result = await slow_operation()
            print(f"结果: {result}")
    except asyncio.TimeoutError:
        print("操作超时!")

# 与wait_for的区别:
# - wait_for: 只影响单个协程
# - timeout: 影响整个代码块内的所有await

# Go对比:
# ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
# result, err := doOperation(ctx)
