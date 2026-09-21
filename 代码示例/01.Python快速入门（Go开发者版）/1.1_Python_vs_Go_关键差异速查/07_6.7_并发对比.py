# ============ 并发对比 ============
# Go: go func() { ... }()
# Python: asyncio
import asyncio

async def async_task():
    await asyncio.sleep(1)
    return "完成"

# 运行
# asyncio.run(async_task())
