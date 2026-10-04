import asyncio
from langchain_core.tools import tool

@tool
async def fetch_url_content(url: str, max_length: int = 1000) -> str:
    """异步获取网页内容
    
    Args:
        url: 网页URL
        max_length: 最大返回长度
        
    Returns:
        网页内容摘要
    """
    # 注意：实际使用需要安装 aiohttp
    # import aiohttp
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(url) as response:
    #         content = await response.text()
    
    # 模拟异步操作
    await asyncio.sleep(0.1)  # 模拟网络延迟
    
    return f"网页 {url} 的内容（模拟），长度: {max_length} 字符"

# 异步调用
async def main():
    result = await fetch_url_content.ainvoke({"url": "https://example.com", "max_length": 500})
    print(result)

asyncio.run(main())
