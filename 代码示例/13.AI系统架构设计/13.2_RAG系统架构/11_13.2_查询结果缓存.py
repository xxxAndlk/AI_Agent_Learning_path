import hashlib
import json
from functools import lru_cache
from typing import Optional, Dict, Any

class QueryCache:
    """查询结果缓存"""
    
    def __init__(self, max_size: int = 1000):
        """
        初始化缓存
        
        参数:
            max_size: 最大缓存数量
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.access_count: Dict[str, int] = {}
    
    def _hash_query(self, query: str) -> str:
        """生成查询哈希"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存结果
        
        参数:
            query: 查询字符串
        
        返回:
            缓存结果或None
        """
        query_hash = self._hash_query(query)
        
        if query_hash in self.cache:
            self.access_count[query_hash] = self.access_count.get(query_hash, 0) + 1
            return self.cache[query_hash]
        
        return None
    
    def set(self, query: str, result: Dict[str, Any]):
        """
        设置缓存
        
        参数:
            query: 查询字符串
            result: 查询结果
        """
        query_hash = self._hash_query(query)
        
        # 如果缓存已满，删除最少使用的项
        if len(self.cache) >= self.max_size:
            min_access = min(self.access_count.values())
            for hash_key, count in self.access_count.items():
                if count == min_access:
                    del self.cache[hash_key]
                    del self.access_count[hash_key]
                    break
        
        self.cache[query_hash] = result
        self.access_count[query_hash] = 1
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_count.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'total_accesses': sum(self.access_count.values())
        }
