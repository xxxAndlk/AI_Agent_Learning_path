"""
模型路由策略实现
支持多种路由算法
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import random

class RoutingStrategy(Enum):
    """61. 路由策略枚举"""
    ROUND_ROBIN = "round_robin"         # 轮询
    RANDOM = "random"                   # 随机
    WEIGHTED = "weighted"               # 加权
    LEAST_LATENCY = "least_latency"     # 最小延迟
    COST_OPTIMIZED = "cost_optimized"   # 成本优化
    QUALITY_OPTIMIZED = "quality"       # 质量优先


@dataclass
class ModelEndpoint:
    """62. 模型端点数据类"""
    name: str
    endpoint: str
    cost_per_1k_tokens: float
    avg_latency_ms: float
    quality_score: float  # 1-5
    weight: float = 1.0
    is_healthy: bool = True


class SmartModelRouter:
    """63. 智能模型路由器
    
    支持多种路由策略，根据需求选择最优路由
    """
    
    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.WEIGHTED):
        self.strategy = strategy
        self.endpoints: Dict[str, List[ModelEndpoint]] = {}
        self.round_robin_counters: Dict[str, int] = {}
    
    def register_endpoint(self, model_family: str, endpoint: ModelEndpoint):
        """64. 注册端点"""
        if model_family not in self.endpoints:
            self.endpoints[model_family] = []
            self.round_robin_counters[model_family] = 0
        
        self.endpoints[model_family].append(endpoint)
    
    def route(
        self,
        model_family: str,
        priority: str = "normal",
        max_cost: Optional[float] = None
    ) -> Optional[ModelEndpoint]:
        """65. 路由到合适的端点
        
        参数:
            model_family: 模型家族（如gpt）
            priority: 优先级（low/normal/high）
            max_cost: 最大成本限制
        返回:
            选中的端点
        """
        if model_family not in self.endpoints:
            return None
        
        # 66. 过滤健康的端点
        candidates = [
            ep for ep in self.endpoints[model_family]
            if ep.is_healthy
        ]
        
        if not candidates:
            return None
        
        # 67. 应用成本过滤
        if max_cost:
            candidates = [ep for ep in candidates if ep.cost_per_1k_tokens <= max_cost]
        
        if not candidates:
            return None
        
        # 68. 根据策略选择
        if self.strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_select(model_family, candidates)
        elif self.strategy == RoutingStrategy.RANDOM:
            return random.choice(candidates)
        elif self.strategy == RoutingStrategy.WEIGHTED:
            return self._weighted_select(candidates)
        elif self.strategy == RoutingStrategy.LEAST_LATENCY:
            return min(candidates, key=lambda x: x.avg_latency_ms)
        elif self.strategy == RoutingStrategy.COST_OPTIMIZED:
            return min(candidates, key=lambda x: x.cost_per_1k_tokens)
        elif self.strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            return max(candidates, key=lambda x: x.quality_score)
        
        return candidates[0]
    
    def _round_robin_select(self, model_family: str, candidates: List[ModelEndpoint]) -> ModelEndpoint:
        """69. 轮询选择"""
        idx = self.round_robin_counters[model_family] % len(candidates)
        self.round_robin_counters[model_family] += 1
        return candidates[idx]
    
    def _weighted_select(self, candidates: List[ModelEndpoint]) -> ModelEndpoint:
        """70. 加权随机选择"""
        total_weight = sum(ep.weight for ep in candidates)
        r = random.uniform(0, total_weight)
        
        current_weight = 0
        for ep in candidates:
            current_weight += ep.weight
            if r <= current_weight:
                return ep
        
        return candidates[-1]


# 使用示例
if __name__ == "__main__":
    router = SmartModelRouter(strategy=RoutingStrategy.COST_OPTIMIZED)
    
    # 71. 注册GPT模型端点
    router.register_endpoint("gpt", ModelEndpoint(
        name="gpt-5.4-mini",
        endpoint="http://localhost:8001",
        cost_per_1k_tokens=0.002,
        avg_latency_ms=200,
        quality_score=3.5,
        weight=2.0
    ))
    
    router.register_endpoint("gpt", ModelEndpoint(
        name="gpt-5.4",
        endpoint="http://localhost:8002",
        cost_per_1k_tokens=0.03,
        avg_latency_ms=500,
        quality_score=4.5,
        weight=1.0
    ))
    
    # 72. 测试路由
    for strategy in RoutingStrategy:
        router.strategy = strategy
        endpoint = router.route("gpt")
        print(f"{strategy.value}: {endpoint.name if endpoint else 'None'}")
