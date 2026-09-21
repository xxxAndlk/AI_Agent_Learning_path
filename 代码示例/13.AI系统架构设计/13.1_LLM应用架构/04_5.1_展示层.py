# 展示层示例
from typing import Optional
from dataclasses import dataclass

@dataclass
class ChatRequest:
    """聊天请求"""
    message: str
    user_id: str
    session_id: str
    metadata: Optional[dict] = None

@dataclass
class ChatResponse:
    """聊天响应"""
    message: str
    session_id: str
    token_usage: dict
    latency_ms: float
    metadata: Optional[dict] = None

class PresentationLayer:
    """展示层"""
    
    def __init__(self, business_layer):
        self.business_layer = business_layer
        
    def handle_chat_request(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        import time
        start_time = time.time()
        
        # 调用业务层
        result = self.business_layer.process_message(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return ChatResponse(
            message=result["response"],
            session_id=request.session_id,
            token_usage=result.get("usage", {}),
            latency_ms=latency_ms
        )
    
    def format_error(self, error: Exception) -> ChatResponse:
        """格式化错误响应"""
        return ChatResponse(
            message=f"抱歉，处理您的请求时发生错误：{str(error)}",
            session_id="",
            token_usage={},
            latency_ms=0
        )
