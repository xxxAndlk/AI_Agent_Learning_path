"""
MCP安全认证模块
支持API密钥、JWT令牌等认证方式
"""

import hashlib
import hmac
import jwt
from typing import Optional, Dict
from datetime import datetime, timedelta
from enum import Enum


class AuthType(str, Enum):
    """认证类型"""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"


class MCPAuthenticator:
    """MCP认证器"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.api_keys: Dict[str, Dict] = {}
        self.blacklist: set = set()
    
    def create_api_key(
        self,
        user_id: str,
        name: str,
        expires_in_days: int = 30
    ) -> str:
        """创建API密钥"""
        import secrets
        
        # 生成随机密钥
        api_key = f"mcp_{secrets.token_urlsafe(32)}"
        
        # 计算密钥哈希
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # 存储密钥信息
        self.api_keys[key_hash] = {
            "user_id": user_id,
            "name": name,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=expires_in_days),
            "is_active": True
        }
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """验证API密钥"""
        # 计算密钥哈希
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # 检查密钥是否存在
        if key_hash not in self.api_keys:
            return None
        
        key_info = self.api_keys[key_hash]
        
        # 检查是否在黑名单
        if key_hash in self.blacklist:
            return None
        
        # 检查是否过期
        if key_info["expires_at"] < datetime.now():
            return None
        
        # 检查是否激活
        if not key_info["is_active"]:
            return None
        
        return key_info
    
    def revoke_api_key(self, api_key: str) -> bool:
        """撤销API密钥"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash in self.api_keys:
            self.blacklist.add(key_hash)
            self.api_keys[key_hash]["is_active"] = False
            return True
        
        return False
    
    def create_jwt_token(
        self,
        user_id: str,
        roles: List[str],
        expires_in_hours: int = 24
    ) -> str:
        """创建JWT令牌"""
        payload = {
            "user_id": user_id,
            "roles": roles,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            
            # 检查是否在黑名单
            if token in self.blacklist:
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token: str):
        """撤销令牌"""
        self.blacklist.add(token)


class MCPSecurityMiddleware:
    """MCP安全中间件"""
    
    def __init__(self, authenticator: MCPAuthenticator):
        self.authenticator = authenticator
    
    def authenticate_request(
        self,
        headers: Dict,
        body: Dict
    ) -> Optional[Dict]:
        """认证请求"""
        # 优先使用API密钥
        api_key = headers.get("X-API-Key")
        if api_key:
            return self.authenticator.verify_api_key(api_key)
        
        # 其次使用JWT
        auth_header = headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return self.authenticator.verify_jwt_token(token)
        
        return None
    
    def authorize_tool_call(
        self,
        user_info: Dict,
        tool_name: str,
        permission_manager: ToolPermission
    ) -> bool:
        """授权工具调用"""
        if not user_info:
            return False
        
        user_roles = user_info.get("roles", [])
        
        # 检查是否有任何角色有权限
        for role in user_roles:
            if permission_manager.check_permission(tool_name, role):
                return True
        
        return False


# 使用示例
auth = MCPAuthenticator(secret_key="your-secret-key")

# 创建API密钥
api_key = auth.create_api_key("user001", "开发环境")
print(f"API密钥: {api_key}")

# 验证API密钥
key_info = auth.verify_api_key(api_key)
print(f"密钥信息: {key_info}")

# 创建JWT令牌
jwt_token = auth.create_jwt_token("user001", ["admin", "developer"])
print(f"JWT令牌: {jwt_token}")
