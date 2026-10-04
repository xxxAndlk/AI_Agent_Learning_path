import json
"""
Token监控系统
实时监控Token使用量和成本
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class TokenUsage:
    """Token使用量"""
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float

class TokenMonitor:
    """Token监控器"""
    
    # 模型定价（每1K tokens）
    PRICING = {
        "gpt-5.4": {"input": 0.03, "output": 0.06},
        "gpt-5.4-mini": {"input": 0.0015, "output": 0.002},
        "gpt-5.4": {"input": 0.005, "output": 0.015},
    }
    
    def __init__(self):
        self.usage_history: List[TokenUsage] = []
        self.daily_quota: int = 1000000  # 每日限额
        self.daily_used: int = 0
        
    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> TokenUsage:
        """记录使用量"""
        pricing = self.PRICING.get(model, {"input": 0.002, "output": 0.002})
        
        cost = (
            prompt_tokens * pricing["input"] / 1000 +
            completion_tokens * pricing["output"] / 1000
        )
        
        usage = TokenUsage(
            timestamp=datetime.now(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost
        )
        
        self.usage_history.append(usage)
        self.daily_used += prompt_tokens + completion_tokens
        
        return usage
    
    def check_quota(self, requested_tokens: int) -> bool:
        """检查是否超出限额"""
        return (self.daily_used + requested_tokens) <= self.daily_quota
    
    def get_usage_report(self) -> Dict:
        """生成使用报告"""
        if not self.usage_history:
            return {"total_cost": 0, "total_tokens": 0}
        
        total_cost = sum(u.cost_usd for u in self.usage_history)
        total_tokens = sum(u.prompt_tokens + u.completion_tokens for u in self.usage_history)
        
        # 按模型分组
        by_model = defaultdict(lambda: {"tokens": 0, "cost": 0})
        for u in self.usage_history:
            by_model[u.model]["tokens"] += u.prompt_tokens + u.completion_tokens
            by_model[u.model]["cost"] += u.cost_usd
        
        return {
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "daily_quota": self.daily_quota,
            "daily_used": self.daily_used,
            "quota_remaining": self.daily_quota - self.daily_used,
            "by_model": dict(by_model)
        }


# 使用示例
if __name__ == "__main__":
    monitor = TokenMonitor()
    
    # 记录使用
    monitor.record_usage("gpt-5.4-mini", 1000, 500)
    monitor.record_usage("gpt-5.4", 500, 1000)
    
    # 生成报告
    report = monitor.get_usage_report()
    print("Token使用报告:", json.dumps(report, indent=2))
