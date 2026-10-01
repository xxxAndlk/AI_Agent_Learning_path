import asyncio
import aiohttp

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """获取单个URL"""
    async with session.get(url) as response:
        return await response.text()

async def fetch_urls(urls: list[str]) -> list[str]:
    """并发获取多个URL"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# 带错误处理的版本
async def fetch_urls_safe(
    urls: list[str],
    timeout: float = 10.0
) -> list[tuple[str, str | None]]:
    """带超时和错误处理"""
    async with aiohttp.ClientSession() as session:
        async def fetch_one(url: str) -> tuple[str, str | None]:
            try:
                async with asyncio.timeout(timeout):
                    async with session.get(url) as response:
                        return (url, await response.text())
            except Exception as e:
                return (url, None)
        
        tasks = [fetch_one(url) for url in urls]
        return await asyncio.gather(*tasks)
