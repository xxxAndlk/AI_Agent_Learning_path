from functools import wraps
from typing import Callable, Any
import time

def cached(ttl: int = 60) -> Callable:
    """
    带过期时间的缓存装饰器
    
    Args:
        ttl: 缓存存活时间（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        cache: dict[str, tuple[Any, float]] = {}
        
        @wraps(func)  # 保留原函数的元信息
        def wrapper(*args, **kwargs) -> Any:
            # 构建缓存键
            cache_key = str((args, frozenset(kwargs.items())))
            
            # 检查缓存是否存在且未过期
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    print(f"Cache hit for {func.__name__}")
                    return result
            
            # 缓存未命中，执行原函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache[cache_key] = (result, time.time())
            return result
        
        return wrapper
    return decorator
