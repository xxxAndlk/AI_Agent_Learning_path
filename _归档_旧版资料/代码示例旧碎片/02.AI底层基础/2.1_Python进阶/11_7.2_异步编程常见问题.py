# 问题代码
async def async_function():
    await asyncio.sleep(1)
    return "Done"

result = async_function()  # ❌ 只返回协程对象，不会执行

# 解决方案
result = asyncio.run(async_function())  # ✅ 正确运行

# 或在已有事件循环中
result = await async_function()
