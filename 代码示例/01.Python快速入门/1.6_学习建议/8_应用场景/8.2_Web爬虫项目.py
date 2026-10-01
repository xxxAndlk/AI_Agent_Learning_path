"""
简单的网页爬虫
提取页面标题和链接
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse

class WebCrawler:
    def __init__(self, max_depth: int = 2, max_pages: int = 100):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited: set[str] = set()
        
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str | None:
        """获取页面内容"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None
    
    def extract_links(self, base_url: str, html: str) -> list[str]:
        """提取页面链接"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # 只保留同域名链接
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.append(full_url)
                
        return links
    
    async def crawl(self, start_url: str) -> dict[str, list[str]]:
        """爬取网站"""
        results = {}
        
        async with aiohttp.ClientSession() as session:
            queue = [(start_url, 0)]
            
            while queue and len(self.visited) < self.max_pages:
                url, depth = queue.pop(0)
                
                if url in self.visited or depth > self.max_depth:
                    continue
                    
                self.visited.add(url)
                print(f"Crawling: {url}")
                
                html = await self.fetch(session, url)
                if html:
                    links = self.extract_links(url, html)
                    results[url] = links
                    
                    for link in links:
                        if link not in self.visited:
                            queue.append((link, depth + 1))
                            
        return results
