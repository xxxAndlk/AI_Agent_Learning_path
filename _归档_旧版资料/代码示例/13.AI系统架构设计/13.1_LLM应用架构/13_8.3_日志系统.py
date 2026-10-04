import logging
from typing import Optional
from datetime import datetime
import json

class StructuredLogger:
    """结构化日志"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 添加JSON格式化处理器
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)
        
    def log_request(
        self,
        request_id: str,
        user_id: str,
        method: str,
        path: str,
        latency_ms: float
    ):
        """记录请求日志"""
        self.logger.info(
            "API Request",
            extra={
                "event_type": "request",
                "request_id": request_id,
                "user_id": user_id,
                "method": method,
                "path": path,
                "latency_ms": latency_ms
            }
        )
        
    def log_llm_call(
        self,
        request_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        error: Optional[str] = None
    ):
        """记录LLM调用日志"""
        self.logger.info(
            "LLM Call",
            extra={
                "event_type": "llm_call",
                "request_id": request_id,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "latency_ms": latency_ms,
                "error": error
            }
        )
        
    def log_error(
        self,
        request_id: str,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None
    ):
        """记录错误日志"""
        self.logger.error(
            "Error",
            extra={
                "event_type": "error",
                "request_id": request_id,
                "error_type": error_type,
                "message": message,
                "stack_trace": stack_trace
            }
        )


class JsonFormatter(logging.Formatter):
    """JSON格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # 添加额外字段
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
            
        for key in ["request_id", "user_id", "model", "latency_ms"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        
        return json.dumps(log_data)


# 使用示例
logger = StructuredLogger("llm-app")
logger.log_request(
    request_id="req_123",
    user_id="user_456",
    method="POST",
    path="/v1/chat/completions",
    latency_ms=1500
)
