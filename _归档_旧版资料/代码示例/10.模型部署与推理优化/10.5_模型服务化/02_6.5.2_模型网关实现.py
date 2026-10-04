"""
模型网关实现
提供统一的模型服务入口和管理功能
"""

from typing import Dict, List, Optional  # 类型提示
from dataclasses import dataclass        # 数据类
from datetime import datetime, timedelta # 时间处理
import hashlib                           # 哈希计算
import json                              # JSON处理

@dataclass
class APIKey:
    """44. API密钥数据类"""
    key_id: str
    key_hash: str
    owner: str
    permissions: List[str]
    rate_limit: int = 100  # 每分钟请求数
    created_at: datetime = None
    expires_at: datetime = None
    is_active: bool = True

class AuthenticationManager:
    """45. 认证管理器
    
    负责API Key的生成、验证和权限管理
    """
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.usage_stats: Dict[str, Dict] = {}
    
    def generate_api_key(self, owner: str, permissions: List[str]) -> str:
        """46. 生成API密钥
        
        参数:
            owner: 密钥所有者
            permissions: 权限列表
        返回:
            生成的API密钥
        """
        # 47. 生成随机密钥
        import secrets
        raw_key = f"sk-{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()[:16]
        
        api_key = APIKey(
            key_id=key_hash,
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            owner=owner,
            permissions=permissions,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=365)
        )
        
        self.api_keys[key_hash] = api_key
        self.usage_stats[key_hash] = {"requests": 0, "tokens": 0, "last_used": None}
        
        return raw_key
    
    def validate_key(self, api_key: str) -> Optional[APIKey]:
        """48. 验证API密钥
        
        参数:
            api_key: 待验证的密钥
        返回:
            密钥信息或None
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        for key_id, key_info in self.api_keys.items():
            if key_info.key_hash == key_hash:
                # 49. 检查是否过期
                if key_info.expires_at and datetime.now() > key_info.expires_at:
                    return None
                
                # 50. 检查是否活跃
                if not key_info.is_active:
                    return None
                
                # 51. 更新使用统计
                self.usage_stats[key_id]["requests"] += 1
                self.usage_stats[key_id]["last_used"] = datetime.now()
                
                return key_info
        
        return None
    
    def check_rate_limit(self, key_id: str) -> bool:
        """52. 检查速率限制"""
        if key_id not in self.api_keys:
            return False
        
        # 简化实现：检查最近一分钟的请求数
        # 实际应该使用Redis等存储
        return True


class ModelRouter:
    """53. 模型路由器
    
    负责将请求路由到不同的模型后端
    """
    
    def __init__(self):
        self.model_backends: Dict[str, Dict] = {}
        self.routing_rules: List[Dict] = []
    
    def register_backend(self, model_name: str, endpoint: str, weight: float = 1.0):
        """54. 注册模型后端"""
        self.model_backends[model_name] = {
            "endpoint": endpoint,
            "weight": weight,
            "healthy": True,
            "latency_ms": 0
        }
    
    def route(self, model_name: str, strategy: str = "round_robin") -> Optional[str]:
        """55. 路由到合适的后端"""
        if model_name not in self.model_backends:
            return None
        
        backend = self.model_backends[model_name]
        
        if not backend["healthy"]:
            return None
        
        return backend["endpoint"]
    
    def health_check(self):
        """56. 健康检查"""
        for model_name, backend in self.model_backends.items():
            # 简化：模拟健康检查
            backend["healthy"] = True


# 使用示例
if __name__ == "__main__":
    # 57. 认证管理器
    auth = AuthenticationManager()
    
    # 58. 生成API密钥
    api_key = auth.generate_api_key(
        owner="user@example.com",
        permissions=["chat", "completion", "embedding"]
    )
    print(f"生成的API密钥: {api_key}")
    
    # 59. 验证密钥
    key_info = auth.validate_key(api_key)
    if key_info:
        print(f"密钥有效，所有者: {key_info.owner}")
        print(f"权限: {key_info.permissions}")
    
    # 60. 模型路由
    router = ModelRouter()
    router.register_backend("gpt-5.4-mini", "http://localhost:8001", weight=1.0)
    router.register_backend("gpt-5.4", "http://localhost:8002", weight=0.5)
    
    endpoint = router.route("gpt-5.4-mini")
    print(f"\n路由到: {endpoint}")
