import asyncio                        # 导入异步IO库，提供协程支持
import aiohttp                        # 导入异步HTTP客户端库，用于并发网络请求

async def fetch_data(url: str, session: aiohttp.ClientSession):
    """异步函数：发送HTTP GET请求并获取数据
    
    参数:
        url: 要请求的API地址
        session: aiohttp会话对象，用于复用连接池
    返回:
        解析后的JSON数据
    """
    async with session.get(url) as response:  # 使用async with进行异步上下文管理
        # response.status 获取HTTP状态码（200表示成功）
        print(f"请求 {url} 完成，状态码: {response.status}")
        # await response.json() 异步等待响应体解析为JSON
        return await response.json()

async def main():
    """主异步函数：协调多个并发请求"""
    # 定义要请求的URL列表（JSONPlaceholder是免费的测试API）
    urls = [
        "https://jsonplaceholder.typicode.com/todos/1",
        "https://jsonplaceholder.typicode.com/todos/2",
        "https://jsonplaceholder.typicode.com/todos/3"
    ]
    # async with创建会话，确保资源正确释放
    async with aiohttp.ClientSession() as session:
        # 使用列表推导式为每个URL创建fetch_data任务
        # 注意：此时任务已创建但尚未执行
        tasks = [fetch_data(url, session) for url in urls]
        # asyncio.gather并发执行所有任务，await等待全部完成
        # return_exceptions=True 表示如果某个任务出错，返回异常而非抛出
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print("所有请求结果:", results)

if __name__ == "__main__":
    # asyncio.run() 是Python 3.7+推荐的运行协程的方式
    # 它会自动创建事件循环、运行协程、关闭循环
    asyncio.run(main())
