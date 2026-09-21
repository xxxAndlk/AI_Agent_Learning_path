"""
RAG缓存策略示例
通过缓存检索结果和生成结果，降低成本和延迟
"""

from typing import Dict, List, Optional, Tuple
import hashlib
import json
from datetime import datetime, timedelta
import numpy as np


class SemanticCache:
    """语义缓存：支持语义相似度匹配的智能缓存"""
    
    def __init__(self, similarity_threshold: float = 0.95, ttl: int = 3600):
        """
        初始化语义缓存
        
        参数:
            similarity_threshold: 相似度阈值，0-1之间，超过此阈值认为缓存命中
                - 值越高，要求越严格，完全相同才命中
                - 值较低时，语义相近的查询也能命中缓存
            ttl: Time To Live，缓存生存时间（秒），超过此时间缓存自动失效
        """
        self.similarity_threshold = similarity_threshold  # 保存相似度阈值
        self.ttl = ttl  # 保存TTL值
        self.cache: Dict[str, Dict] = {}  # 缓存存储，使用字典实现
        self.access_count = 0  # 缓存访问总次数
        self.hit_count = 0  # 缓存命中次数
    
    def _get_cache_key(self, query: str) -> str:
        """
        生成缓存key：使用MD5哈希将查询字符串转换为固定长度的key
        
        参数:
            query: 查询字符串
        返回:
            32位的MD5哈希字符串作为缓存键
        """
        return hashlib.md5(query.encode()).hexdigest()
    
    def _compute_similarity(self, query1: str, query2: str) -> float:
        """
        计算两个查询的相似度（使用Jaccard相似度）
        
        参数:
            query1: 第一个查询字符串
            query2: 第二个查询字符串
        返回:
            相似度分数，0-1之间
        """
        # 将查询分词为词集合
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        # 处理空输入
        if not words1 or not words2:
            return 0.0
        
        # 计算Jaccard相似度：|A ∩ B| / |A ∪ B|
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def get(self, query: str, query_embedding: Optional[np.ndarray] = None) -> Optional[Dict]:
        """
        从缓存获取结果
        
        实现逻辑：
        1. 首先尝试精确匹配（通过MD5 key）
        2. 如果未命中，遍历缓存进行语义相似度匹配
        
        参数:
            query: 查询字符串
            query_embedding: 查询向量（可选，用于更精确的语义匹配）
        返回:
            缓存的结果字典，如果未命中返回None
        """
        self.access_count += 1  # 增加访问计数
        
        # 第1步：尝试精确匹配
        cache_key = self._get_cache_key(query)
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # 检查缓存是否过期：比较当前时间与缓存创建时间的差值
            if datetime.now() - entry["timestamp"] < timedelta(seconds=self.ttl):
                # 缓存命中！增加命中计数和访问次数
                self.hit_count += 1
                entry["access_count"] += 1
                return entry["result"]
            else:
                # 缓存已过期，删除该条目
                del self.cache[cache_key]
        
        # 第2步：语义相似度匹配（精确匹配未命中时）
        for key, entry in self.cache.items():
            # 检查该缓存条目是否过期
            if datetime.now() - entry["timestamp"] >= timedelta(seconds=self.ttl):
                continue  # 跳过过期缓存
            
            # 计算当前查询与缓存查询的相似度
            similarity = self._compute_similarity(query, entry["query"])
            
            # 如果相似度超过阈值，认为缓存命中
            if similarity >= self.similarity_threshold:
                self.hit_count += 1
                entry["access_count"] += 1
                return entry["result"]
        
        # 没有任何命中，返回None
        return None
    
    def set(self, query: str, result: Dict, query_embedding: Optional[np.ndarray] = None):
        """
        设置缓存：存储查询和对应的结果
        
        参数:
            query: 查询字符串
            result: 需要缓存的结果数据（可以是任何类型）
            query_embedding: 查询向量（可选，用于后续更精确的匹配）
        """
        # 生成缓存key
        cache_key = self._get_cache_key(query)
        
        # 存储缓存条目，包含：
        # - query: 原始查询（用于后续相似度计算）
        # - result: 缓存的结果
        # - timestamp: 创建时间（用于判断过期）
        # - access_count: 访问次数统计
        # - embedding: 查询向量（可选）
        self.cache[cache_key] = {
            "query": query,
            "result": result,
            "timestamp": datetime.now(),
            "access_count": 0,
            "embedding": query_embedding
        }
    
    def get_stats(self) -> Dict:
        """
        获取缓存统计信息
        
        返回:
            包含缓存命中率、条目数等信息的字典
        """
        # 计算命中率
        hit_rate = self.hit_count / self.access_count if self.access_count > 0 else 0
        
        return {
            "total_entries": len(self.cache),  # 当前缓存条目数
            "access_count": self.access_count,  # 总访问次数
            "hit_count": self.hit_count,  # 命中次数
            "hit_rate": hit_rate,  # 命中率
            "ttl": self.ttl  # TTL设置
        }
    
    def clear_expired(self):
        """
        清理所有过期缓存
        
        返回:
            清理的过期条目数量
        """
        now = datetime.now()
        
        # 找出所有过期的缓存key
        expired_keys = [
            key for key, entry in self.cache.items()
            if now - entry["timestamp"] >= timedelta(seconds=self.ttl)
        ]
        
        # 删除过期缓存
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


class RAGCacheManager:
    """RAG缓存管理器：管理检索缓存和生成缓存，提供统一的缓存接口"""
    
    def __init__(self):
        """初始化缓存管理器"""
        # 第1层缓存：检索结果缓存
        # 相似度阈值0.90（较宽松，因为检索结果相对稳定）
        # TTL 1小时（检索结果通常变化较少）
        self.retrieval_cache = SemanticCache(
            similarity_threshold=0.90,
            ttl=3600
        )
        
        # 第2层缓存：生成结果缓存
        # 相似度阈值0.95（较严格，因为生成结果需要精确匹配）
        # TTL 30分钟（生成结果可能需要更及时更新）
        self.generation_cache = SemanticCache(
            similarity_threshold=0.95,
            ttl=1800
        )
        
        # 成本统计：用于计算节省的token和API调用
        self.token_saved = 0  # 节省的token数量
        self.api_calls_saved = 0  # 节省的API调用次数
    
    def get_cached_retrieval(self, query: str) -> Optional[List[Dict]]:
        """
        获取缓存的检索结果
        
        参数:
            query: 查询字符串
        返回:
            缓存的检索结果（文档列表），未命中返回None
        """
        result = self.retrieval_cache.get(query)
        if result:
            # 命中缓存，节省了一次检索计算
            self.api_calls_saved += 1
        return result
    
    def cache_retrieval(self, query: str, documents: List[Dict]):
        """
        缓存检索结果
        
        参数:
            query: 查询字符串
            documents: 检索返回的文档列表
        """
        self.retrieval_cache.set(query, documents)
    
    def get_cached_generation(self, query: str) -> Optional[str]:
        """
        获取缓存的生成结果
        
        参数:
            query: 查询字符串
        返回:
            缓存的生成结果（答案字符串），未命中返回None
        """
        result = self.generation_cache.get(query)
        if result and isinstance(result, str):
            # 命中缓存，节省了token和API调用
            self.token_saved += len(result.split())  # 估算节省的token数
            self.api_calls_saved += 1
        return result
    
    def cache_generation(self, query: str, answer: str):
        """
        缓存生成结果
        
        参数:
            query: 查询字符串
            answer: LLM生成的答案
        """
        self.generation_cache.set(query, answer)
    
    def get_cost_savings(self) -> Dict:
        """
        获取成本节省统计
        
        返回:
            包含各项成本节省指标的字典
        """
        # 获取两个缓存的统计信息
        retrieval_stats = self.retrieval_cache.get_stats()
        generation_stats = self.generation_cache.get_stats()
        
        # 假设每次API调用成本$0.002，计算总节省成本
        estimated_cost = self.api_calls_saved * 0.002
        
        return {
            "token_saved": self.token_saved,  # 节省的token数
            "api_calls_saved": self.api_calls_saved,  # 节省的API调用次数
            "retrieval_cache": retrieval_stats,  # 检索缓存统计
            "generation_cache": generation_stats,  # 生成缓存统计
            "estimated_cost_saved": estimated_cost  # 估算节省的成本（美元）
        }


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 创建RAG缓存管理器实例
    cache_manager = RAGCacheManager()
    
    # 模拟查询场景
    query1 = "什么是机器学习？"
    
    # 第1次查询：缓存未命中，需要执行实际检索
    result = cache_manager.get_cached_retrieval(query1)
    if not result:
        print(f"缓存未命中: {query1}")
        # 模拟执行检索过程
        documents = [{"doc": "机器学习是AI的一个分支"}]
        # 将结果存入缓存
        cache_manager.cache_retrieval(query1, documents)
    
    # 相似查询：缓存应该命中（因为查询非常相似）
    query2 = "什么是机器学习"  # 少了一个问号
    result = cache_manager.get_cached_retrieval(query2)
    if result:
        print(f"缓存命中: {query2}")
    
    # 查看缓存统计信息
    stats = cache_manager.get_cost_savings()
    print(f"\n缓存统计:")
    print(f"  检索缓存命中率: {stats['retrieval_cache']['hit_rate']:.2%}")
    print(f"  API调用节省: {stats['api_calls_saved']}")
