# 错误1：在async函数中使用同步IO
async def bad_example():
    import requests  # 同步库
    response = requests.get(url)  # 阻塞整个事件循环！
    
# 正确：使用aiohttp
async def good_example():
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)  # 非阻塞

# 错误2：忘记await
async def bad_call():
    result = async_func()  # 返回协程对象，不是结果！
    
# 正确
async def good_call():
    result = await async_func()  # 等待完成

# 错误3：在协程中使用线程锁
lock = threading.Lock()

async def bad_lock():
    with lock:  # 可能阻塞事件循环
        await something()
        
# 正确：使用asyncio.Lock
lock = asyncio.Lock()

async def good_lock():
    async with lock:  # 不会阻塞事件循环
        await something()
