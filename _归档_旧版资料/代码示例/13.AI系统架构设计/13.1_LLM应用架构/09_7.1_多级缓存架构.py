from typing import Optional, Any
import json
import hashlib

class CacheManager:
    """缓存管理器（多级缓存）"""
    
    def __init__(self):
        # L1: 内存缓存
        self.l1_cache = {}  # {key: (value, expiry)}
        
        # L2: Redis缓存
        self.redis_client = None
        self.redis_enabled = False
        
        # 配置
        self.l1_ttl = 300  # L1缓存5分钟
        self.l2_ttl = 3600  # L2缓存1小时
        
    def enable_redis(self, host: str = "localhost", port: int = 6379):
        """启用Redis缓存"""
        import redis
        try:
            self.redis_client = redis.Redis(
                host=host, 
                port=port, 
                decode_responses=True
            )
            self.redis_enabled = True
        except:
            print("Redis连接失败，使用内存缓存")
            
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        # L1查询
        if key in self.l1_cache:
            value, expiry = self.l1_cache[key]
            if expiry > datetime.now():
                return value
            else:
                del self.l1_cache[key]
        
        # L2查询
        if self.redis_enabled and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    # 回填L1
                    self.l1_cache[key] = (
                        value, 
                        datetime.now() + timedelta(seconds=self.l1_ttl)
                    )
                    return value
            except:
                pass
                
        return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None):
        """设置缓存"""
        # L1设置
        ttl = ttl or self.l1_ttl
        self.l1_cache[key] = (
            value, 
            datetime.now() + timedelta(seconds=ttl)
        )
        
        # L2设置
        if self.redis_enabled and self.redis_client:
            try:
                l2_ttl = ttl * self.l2_ttl // self.l1_ttl
                self.redis_client.setex(key, l2_ttl, value)
            except:
                pass
    
    def delete(self, key: str):
        """删除缓存"""
        # L1删除
        self.l1_cache.pop(key, None)
        
        # L2删除
        if self.redis_enabled and self.redis_client:
            try:
                self.redis_client.delete(key)
            except:
                pass
    
    def clear_l1(self):
        """清空L1缓存"""
        self.l1_cache.clear()
        
    def clear_all(self):
        """清空所有缓存"""
        self.l1_cache.clear()
        if self.redis_enabled and self.redis_client:
            try:
                self.redis_client.flushdb()
            except:
                pass


class ResponseCache:
    """响应缓存"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        
    def generate_cache_key(
        self,
        prompt: str,
        model: str,
        temperature: float,
        **kwargs
    ) -> str:
        """生成缓存键"""
        # 排除随机参数
        key_parts = [
            prompt,
            model,
            str(temperature)
        ]
        for k, v in sorted(kwargs.items()):
            if k not in ["stream", "functions"]:
                key_parts.append(f"{k}:{v}")
        
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def cache_response(
        self,
        prompt: str,
        response: str,
        model: str,
        temperature: float,
        **kwargs
    ):
        """缓存响应"""
        key = self.generate_cache_key(prompt, model, temperature, **kwargs)
        self.cache.set(key, response)
        
    def get_cached_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        **kwargs
    ) -> Optional[str]:
        """获取缓存响应"""
        key = self.generate_cache_key(prompt, model, temperature, **kwargs)
        return self.cache.get(key)
