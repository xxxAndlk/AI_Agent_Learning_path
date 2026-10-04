# 异步上下文管理器
class AsyncContextManager:
    async def __aenter__(self):
        # 获取资源
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 释放资源
        pass

# 异步迭代器
class AsyncIterator:
    async def __aiter__(self):
        return self
    
    async def __anext__(self):
        # 异步获取下一个值
        raise StopAsyncIteration

# 异步生成器
async def async_generator():
    for item in items:
        await process(item)  # 异步处理
        yield item           # 产出结果
