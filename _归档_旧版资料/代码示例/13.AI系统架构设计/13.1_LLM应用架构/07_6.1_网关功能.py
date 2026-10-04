from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import time

@dataclass
class APIRequest:
    """API请求"""
    method: str
    path: str
    headers: dict
    query_params: dict
    body: Optional[dict]
    client_ip: str
    timestamp: datetime

@dataclass
class APIResponse:
    """API响应"""
    status_code: int
    body: dict
    headers: dict = None

class RateLimiter:
    """限流器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {client_id: [timestamp1, timestamp2, ...]}
        
    def is_allowed(self, client_id: str) -> bool:
        """检查请求是否允许"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # 清理过期记录
        if client_id in self.requests:
            self.requests[client_id] = [
                ts for ts in self.requests[client_id] if ts > window_start
            ]
        else:
            self.requests[client_id] = []
        
        # 检查是否超限
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # 记录请求
        self.requests[client_id].append(now)
        return True

class Authenticator:
    """认证器"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.valid_tokens = {}  # {token: expiry}
        
    def verify_token(self, token: str) -> bool:
        """验证Token"""
        if token in self.valid_tokens:
            return self.valid_tokens[token] > datetime.now()
        return False
    
    def generate_token(self, user_id: str, ttl_hours: int = 24) -> str:
        """生成Token"""
        token = hashlib.sha256(
            f"{user_id}:{time.time()}:{self.secret_key}".encode()
        ).hexdigest()
        
        expiry = datetime.now() + timedelta(hours=ttl_hours)
        self.valid_tokens[token] = expiry
        return token

class APIGateway:
    """API网关"""
    
    def __init__(self, config: dict):
        self.config = config
        self.rate_limiter = RateLimiter(
            max_requests=config.get("rate_limit", 100),
            window_seconds=config.get("rate_window", 60)
        )
        self.authenticator = Authenticator(config["secret_key"])
        self.routes = {}
        self.middlewares = []
        
    def register_route(self, path: str, handler: Callable):
        """注册路由"""
        self.routes[path] = handler
        
    def add_middleware(self, middleware: Callable):
        """添加中间件"""
        self.middlewares.append(middleware)
        
    def handle_request(self, request: APIRequest) -> APIResponse:
        """处理请求"""
        
        # 1. 限流检查
        client_id = request.client_ip
        if not self.rate_limiter.is_allowed(client_id):
            return APIResponse(
                status_code=429,
                body={"error": "Too Many Requests"}
            )
        
        # 2. 认证检查（对于需要认证的路由）
        if self._requires_auth(request.path):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not self.authenticator.verify_token(token):
                return APIResponse(
                    status_code=401,
                    body={"error": "Unauthorized"}
                )
        
        # 3. 执行中间件
        for middleware in self.middlewares:
            request = middleware(request)
            if isinstance(request, APIResponse):
                return request
        
        # 4. 路由到后端服务
        handler = self.routes.get(request.path)
        if not handler:
            return APIResponse(
                status_code=404,
                body={"error": "Not Found"}
            )
        
        try:
            return handler(request)
        except Exception as e:
            return APIResponse(
                status_code=500,
                body={"error": str(e)}
            )
    
    def _requires_auth(self, path: str) -> bool:
        """检查路径是否需要认证"""
        public_paths = ["/health", "/ping", "/v1/public"]
        return path not in public_paths
