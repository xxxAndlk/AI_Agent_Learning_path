import time
import json
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Callable

class ModelMonitor:
    """模型监控系统
    
    功能：
    - 实时性能监控
    - 延迟追踪
    - 简单的数据漂移检测
    """
    def __init__(self, window_size: int = 1000):
        """
        参数:
            window_size: 滑动窗口大小
        """
        self.window_size = window_size
        self.metrics = {
            "latency": deque(maxlen=window_size),           # 延迟（ms）
            "throughput": deque(maxlen=window_size),        # 吞吐量（req/s）
            "errors": deque(maxlen=window_size),            # 错误数
            "predictions": deque(maxlen=window_size),       # 预测分布
            "input_stats": deque(maxlen=window_size),       # 输入统计
        }
        self.start_time = time.time()
        self.total_requests = 0
    
    def record_latency(self, latency_ms: float):
        """记录请求延迟"""
        self.metrics["latency"].append({
            "value": latency_ms,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_prediction(self, prediction):
        """记录预测结果"""
        self.metrics["predictions"].append({
            "value": prediction,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_error(self, error_msg: str):
        """记录错误"""
        self.metrics["errors"].append({
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_statistics(self) -> Dict:
        """获取监控统计信息"""
        stats = {
            "total_requests": self.total_requests,
            "uptime_seconds": time.time() - self.start_time,
            "error_count": len(self.metrics["errors"]),
        }
        
        # 延迟统计
        if self.metrics["latency"]:
            latencies = [m["value"] for m in self.metrics["latency"]]
            stats["latency"] = {
                "mean": sum(latencies) / len(latencies),
                "min": min(latencies),
                "max": max(latencies),
                "p95": sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max(latencies)
            }
        
        # 预测分布
        if self.metrics["predictions"]:
            predictions = [m["value"] for m in self.metrics["predictions"]]
            stats["prediction_distribution"] = self._calculate_distribution(predictions)
        
        return stats
    
    def _calculate_distribution(self, values: List) -> Dict:
        """计算分布统计"""
        if not values:
            return {}
        
        if isinstance(values[0], (int, float)):
            # 数值型：计算均值、方差
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            return {
                "mean": mean,
                "variance": variance,
                "count": len(values)
            }
        else:
            # 类别型：计算频次
            freq = {}
            for v in values:
                freq[v] = freq.get(v, 0) + 1
            return freq
    
    def check_alerts(self) -> List[str]:
        """检查告警条件"""
        alerts = []
        
        # 检查延迟
        if self.metrics["latency"]:
            latencies = [m["value"] for m in self.metrics["latency"]]
            avg_latency = sum(latencies) / len(latencies)
            if avg_latency > 1000:  # 超过1秒
                alerts.append(f"平均延迟过高: {avg_latency:.2f}ms")
        
        # 检查错误率
        if self.total_requests > 0:
            error_rate = len(self.metrics["errors"]) / self.total_requests
            if error_rate > 0.05:  # 超过5%
                alerts.append(f"错误率过高: {error_rate*100:.2f}%")
        
        return alerts

class PerformanceDecorator:
    """性能监控装饰器"""
    def __init__(self, monitor: ModelMonitor):
        self.monitor = monitor
    
    def __call__(self, func):
        """装饰器实现"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                latency = (time.time() - start_time) * 1000  # 转为ms
                self.monitor.record_latency(latency)
                self.monitor.total_requests += 1
                
                # 如果结果是分类结果，记录预测
                if isinstance(result, (int, str)):
                    self.monitor.record_prediction(result)
                
                return result
            
            except Exception as e:
                self.monitor.record_error(str(e))
                raise
        
        return wrapper

if __name__ == "__main__":
    # 创建监控器
    monitor = ModelMonitor()
    
    # 模拟监控数据
    import random
    
    for i in range(100):
        # 模拟延迟（大部分正常，偶尔有延迟）
        if random.random() < 0.9:
            latency = random.uniform(50, 150)
        else:
            latency = random.uniform(500, 2000)
        
        monitor.record_latency(latency)
        monitor.total_requests += 1
        
        # 模拟预测
        monitor.record_prediction(random.choice(["A", "B", "C"]))
        
        # 模拟错误
        if random.random() < 0.02:
            monitor.record_error("Random error")
    
    # 获取统计
    stats = monitor.get_statistics()
    print("=== 监控统计 ===")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # 检查告警
    alerts = monitor.check_alerts()
    if alerts:
        print("\n=== 告警信息 ===")
        for alert in alerts:
            print(alert)
