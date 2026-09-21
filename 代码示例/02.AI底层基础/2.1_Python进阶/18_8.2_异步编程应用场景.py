import asyncio
from typing import AsyncIterator

class AsyncDataLoader:
    """异步数据加载器，适用于大规模数据集"""
    
    def __init__(self, file_paths: list, batch_size: int = 32):
        self.file_paths = file_paths
        self.batch_size = batch_size
    
    async def __aiter__(self):
        """异步迭代器"""
        batch = []
        for path in self.file_paths:
            data = await self._load_file(path)  # 异步加载
            batch.append(data)
            if len(batch) >= self.batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
    
    async def _load_file(self, path: str):
        """异步文件加载"""
        # 实际应用中使用aiofiles等异步文件库
        await asyncio.sleep(0.01)  # 模拟IO延迟
        return f"data from {path}"
