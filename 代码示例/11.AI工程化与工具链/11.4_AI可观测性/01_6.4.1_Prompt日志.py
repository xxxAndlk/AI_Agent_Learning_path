"""
Prompt日志系统实现
记录LLM交互的完整输入输出
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib

@dataclass
class PromptLogEntry:
    """Prompt日志条目"""
    log_id: str
    timestamp: datetime
    model: str                          # 使用的模型
    prompt: str                         # 输入Prompt
    completion: str                     # 模型输出
    prompt_tokens: int                  # Prompt token数
    completion_tokens: int              # 输出token数
    total_tokens: int                   # 总token数
    latency_ms: float                   # 延迟（毫秒）
    user_id: Optional[str] = None       # 用户ID
    session_id: Optional[str] = None    # 会话ID
    tags: Optional[Dict] = None         # 自定义标签
    prompt_hash: Optional[str] = None   # Prompt哈希（用于去重）

class PromptLogger:
    """Prompt日志记录器"""
    
    def __init__(self, max_logs: int = 10000):
        self.logs: List[PromptLogEntry] = []
        self.max_logs = max_logs
        self.log_counter = 0
        self.sensitive_keywords = ["password", "secret", "token", "api_key"]
    
    def _calculate_hash(self, text: str) -> str:
        """计算文本哈希"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def _sanitize_text(self, text: str) -> str:
        """脱敏处理"""
        # 移除敏感信息
        for keyword in self.sensitive_keywords:
            text = text.replace(keyword, "[REDACTED]")
        return text
    
    def log(
        self,
        model: str,
        prompt: str,
        completion: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[Dict] = None
    ) -> PromptLogEntry:
        """记录Prompt日志"""
        self.log_counter += 1
        
        # 脱敏处理
        safe_prompt = self._sanitize_text(prompt)
        safe_completion = self._sanitize_text(completion)
        
        entry = PromptLogEntry(
            log_id=f"pl_{self.log_counter}",
            timestamp=datetime.now(),
            model=model,
            prompt=safe_prompt,
            completion=safe_completion,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            user_id=user_id,
            session_id=session_id,
            tags=tags or {},
            prompt_hash=self._calculate_hash(safe_prompt)
        )
        
        self.logs.append(entry)
        
        # 限制日志数量
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        
        return entry
    
    def query(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[PromptLogEntry]:
        """查询日志"""
        results = []
        for log in reversed(self.logs):  # 从新到旧
            if user_id and log.user_id != user_id:
                continue
            if session_id and log.session_id != session_id:
                continue
            if model and log.model != model:
                continue
            if start_time and log.timestamp < start_time:
                continue
            results.append(log)
            if len(results) >= limit:
                break
        return results
    
    def get_stats(self, hours: int = 24) -> Dict:
        """获取统计信息"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [l for l in self.logs if l.timestamp > cutoff]
        
        if not recent:
            return {"total": 0}
        
        total_prompt_tokens = sum(l.prompt_tokens for l in recent)
        total_completion_tokens = sum(l.completion_tokens for l in recent)
        avg_latency = sum(l.latency_ms for l in recent) / len(recent)
        
        # Prompt去重统计
        unique_prompts = len(set(l.prompt_hash for l in recent))
        
        return {
            "period_hours": hours,
            "total_calls": len(recent),
            "unique_prompts": unique_prompts,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "avg_latency_ms": round(avg_latency, 2),
            "cache_hit_rate": (1 - unique_prompts / len(recent)) if recent else 0
        }


# 使用示例
if __name__ == "__main__":
    logger = PromptLogger()
    
    # 模拟记录
    for i in range(10):
        logger.log(
            model="gpt-5.4-mini",
            prompt=f"What is {i}?",
            completion=f"This is the answer for {i}",
            prompt_tokens=5,
            completion_tokens=10,
            latency_ms=100 + i * 10,
            user_id="user_001",
            session_id="session_001",
            tags={"category": "test"}
        )
    
    # 查询统计
    stats = logger.get_stats()
    print("Prompt日志统计:", json.dumps(stats, indent=2))
