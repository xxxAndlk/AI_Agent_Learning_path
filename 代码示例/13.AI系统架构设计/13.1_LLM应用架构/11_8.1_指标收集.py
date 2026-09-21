from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import time
import threading

@dataclass
class MetricsData:
    """指标数据"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics: List[MetricsData] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.lock = threading.Lock()
        
    def increment_counter(self, name: str, value: float = 1, tags: Dict = None):
        """增加计数器"""
        with self.lock:
            key = self._make_key(name, tags)
            self.counters[key] = self.counters.get(key, 0) + value
            
    def set_gauge(self, name: str, value: float, tags: Dict = None):
        """设置仪表值"""
        with self.lock:
            key = self._make_key(name, tags)
            self.gauges[key] = value
            
    def record_histogram(self, name: str, value: float, tags: Dict = None):
        """记录直方图"""
        with self.lock:
            key = self._make_key(name, tags)
            if key not in self.histograms:
                self.histograms[key] = []
            self.histograms[key].append(value)
            
            # 保持最近1000条记录
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]
    
    def _make_key(self, name: str, tags: Dict = None) -> str:
        """生成指标键"""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"
    
    def get_metrics(self) -> Dict:
        """获取所有指标"""
        with self.lock:
            return {
                "counters": self.counters.copy(),
                "gauges": self.gauges.copy(),
                "histograms": {
                    k: {
                        "count": len(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                        "avg": sum(v) / len(v) if v else 0,
                        "p50": self._percentile(v, 0.5),
                        "p95": self._percentile(v, 0.95),
                        "p99": self._percentile(v, 0.99),
                    }
                    for k, v in self.histograms.items()
                }
            }
    
    def _percentile(self, values: List[float], p: float) -> float:
        """计算百分位数"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * p)
        return sorted_values[min(index, len(sorted_values) - 1)]


# 全局指标收集器
metrics_collector = MetricsCollector()


class LLMMetrics:
    """LLM指标工具"""
    
    @staticmethod
    def record_request(model: str, latency_ms: float, tokens: int):
        """记录LLM请求"""
        metrics_collector.increment_counter(
            "llm.requests.total",
            tags={"model": model}
        )
        
        metrics_collector.record_histogram(
            "llm.latency_ms",
            latency_ms,
            tags={"model": model}
        )
        
        metrics_collector.record_histogram(
            "llm.tokens",
            tokens,
            tags={"model": model}
        )
        
    @staticmethod
    def record_error(error_type: str):
        """记录错误"""
        metrics_collector.increment_counter(
            "llm.errors.total",
            tags={"type": error_type}
        )
        
    @staticmethod
    def record_cache_hit(cache_type: str):
        """记录缓存命中"""
        metrics_collector.increment_counter(
            "cache.hits.total",
            tags={"type": cache_type}
        )
