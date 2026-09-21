class RouteConfig:
    """路由配置"""
    
    # 路由定义
    ROUTES = {
        # 健康检查
        "GET /health": {"handler": "health_check", "auth": False},
        
        # 聊天接口
        "POST /v1/chat/completions": {
            "handler": "chat_completions", 
            "auth": True,
            "rate_limit": 60
        },
        
        # 流式聊天
        "POST /v1/chat/completions/stream": {
            "handler": "chat_completions_stream",
            "auth": True,
            "rate_limit": 30
        },
        
        # 向量检索
        "POST /v1/embeddings": {
            "handler": "create_embeddings",
            "auth": True,
            "rate_limit": 100
        },
        
        # 会话管理
        "GET /v1/sessions": {"handler": "list_sessions", "auth": True},
        "DELETE /v1/sessions/{id}": {"handler": "delete_session", "auth": True},
    }
    
    @classmethod
    def get_handler(cls, method: str, path: str) -> Optional[dict]:
        """获取路由处理器"""
        key = f"{method} {path}"
        return cls.ROUTES.get(key)
