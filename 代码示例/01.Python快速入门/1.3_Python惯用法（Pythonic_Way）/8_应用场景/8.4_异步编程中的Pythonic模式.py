import asyncio

# 异步生成器
async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

# 异步推导式（Python 3.6+）
async def main():
    result = [x async for x in async_range(10)]
    # 异步生成器表达式
    total = sum(x async for x in async_range(100))

asyncio.run(main())
