from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Type, Optional
import functools
import time

class CachedTool(BaseTool):
    """带缓存的工具基类"""
    
    name: str = "cached_tool"
    description: str = "带缓存的工具"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = {}
        self._cache_ttl = 300  # 缓存有效期（秒）
    
    def _generate_cache_key(self, **kwargs) -> str:
        """生成缓存键"""
        return str(sorted(kwargs.items()))
    
    def _get_cached(self, key: str) -> Optional[str]:
        """获取缓存"""
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return result
            else:
                del self._cache[key]
        return None
    
    def _set_cached(self, key: str, value: str):
        """设置缓存"""
        self._cache[key] = (value, time.time())

class OptimizedSearchTool(CachedTool):
    """优化的搜索工具"""
    
    name: str = "optimized_search"
    description: str = "高性能搜索工具"
    
    def _run(self, query: str, use_cache: bool = True) -> str:
        # 检查缓存
        cache_key = self._generate_cache_key(query=query)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return f"[缓存] {cached}"
        
        # 执行搜索
        result = f"搜索结果: {query}"
        
        # 设置缓存
        if use_cache:
            self._set_cached(cache_key, result)
        
        return result
