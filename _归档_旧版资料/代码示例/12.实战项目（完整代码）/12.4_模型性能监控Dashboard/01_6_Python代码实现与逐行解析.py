# 导入类型注解和标准库
from typing import Dict, List, Deque
from collections import deque
from datetime import datetime, timedelta
import json
import time
import threading

class ModelPerformanceMonitor:
    """模型性能监控器
    
    功能：
    - 实时性能指标采集：记录每次请求的延迟和结果
    - 告警规则配置：支持多种告警条件
    - 历史趋势分析：提供时间序列数据
    - 指标可视化数据准备：输出Dashboard所需数据
    """
    def __init__(self, window_size: int = 1000):
        """
        参数:
            window_size: 滑动窗口大小，控制存储的指标数量
        """
        self.window_size = window_size
        
        # 指标存储：使用deque实现滑动窗口
        self.metrics = {
            "latency": deque(maxlen=window_size),      # 延迟记录
            "throughput": deque(maxlen=window_size),  # 吞吐量记录
            "requests": deque(maxlen=window_size),   # 请求记录
            "errors": deque(maxlen=window_size),      # 错误记录
            "predictions": deque(maxlen=window_size)  # 预测结果记录
        }
        
        # 告警规则：配置各类告警的触发条件
        self.alert_rules = {
            "latency_high": {"threshold": 1000, "operator": "gt"},      # 延迟>1000ms告警
            "error_rate_high": {"threshold": 0.05, "operator": "gt"},  # 错误率>5%告警
            "throughput_low": {"threshold": 10, "operator": "lt"}      # 吞吐量<10告警
        }
        
        # 告警历史：存储所有触发的告警记录
        self.alerts: List[Dict] = []
        
        # 统计信息：维护全局统计变量
        self.start_time = datetime.now()
        self.total_requests = 0
        self.total_errors = 0
    
    def record_request(self, latency_ms: float, success: bool = True, prediction=None):
        """记录请求：采集单次请求的性能数据
        
        参数:
            latency_ms: 请求延迟（毫秒）
            success: 请求是否成功
            prediction: 预测结果（可选）
        """
        timestamp = datetime.now()
        
        # 记录延迟
        self.metrics["latency"].append({
            "value": latency_ms,
            "timestamp": timestamp.isoformat()
        })
        
        # 记录请求
        self.metrics["requests"].append({
            "success": success,
            "timestamp": timestamp.isoformat()
        })
        self.total_requests += 1
        
        # 记录错误
        if not success:
            self.metrics["errors"].append({
                "timestamp": timestamp.isoformat()
            })
            self.total_errors += 1
        
        # 记录预测
        if prediction is not None:
            self.metrics["predictions"].append({
                "value": prediction,
                "timestamp": timestamp.isoformat()
            })
        
        # 每次记录后检查告警条件
        self._check_alerts()
    
    def _check_alerts(self):
        """检查告警条件：评估是否需要触发告警"""
        current_time = datetime.now()
        
        # 检查延迟告警
        if self.metrics["latency"]:
            latencies = [m["value"] for m in self.metrics["latency"]]
            avg_latency = sum(latencies) / len(latencies)
            
            if avg_latency > self.alert_rules["latency_high"]["threshold"]:
                self._trigger_alert(
                    "latency_high",
                    f"平均延迟过高: {avg_latency:.2f}ms",
                    severity="warning"
                )
        
        # 检查错误率告警（需要至少100个请求）
        if self.total_requests > 100:
            error_rate = self.total_errors / self.total_requests
            if error_rate > self.alert_rules["error_rate_high"]["threshold"]:
                self._trigger_alert(
                    "error_rate_high",
                    f"错误率过高: {error_rate*100:.2f}%",
                    severity="critical"
                )
    
    def _trigger_alert(self, rule_name: str, message: str, severity: str = "warning"):
        """触发告警：记录告警并防止重复告警
        
        参数:
            rule_name: 告警规则名称
            message: 告警消息内容
            severity: 告警级别
        """
        # 防止重复告警（5分钟内同一规则只告警一次）
        recent_alerts = [
            a for a in self.alerts 
            if a["rule"] == rule_name 
            and datetime.now() - datetime.fromisoformat(a["timestamp"]) < timedelta(minutes=5)
        ]
        
        if not recent_alerts:
            alert = {
                "rule": rule_name,
                "message": message,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
            self.alerts.append(alert)
            print(f"🚨 告警 [{severity.upper()}]: {message}")
    
    def get_realtime_stats(self) -> Dict:
        """获取实时统计：计算并返回当前性能指标
        
        返回:
            包含各类统计指标的字典
        """
        stats = {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / self.total_requests if self.total_requests > 0 else 0
        }
        
        # 延迟统计：计算均值、最值和P95分位数
        if self.metrics["latency"]:
            latencies = [m["value"] for m in self.metrics["latency"]]
            sorted_latencies = sorted(latencies)
            stats["latency"] = {
                "mean": sum(latencies) / len(latencies),
                "min": min(latencies),
                "max": max(latencies),
                "p95": sorted_latencies[int(len(latencies) * 0.95)]
            }
        
        # 吞吐量（最近1分钟）
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_requests = [
            m for m in self.metrics["requests"]
            if datetime.fromisoformat(m["timestamp"]) > one_minute_ago
        ]
        stats["throughput_rpm"] = len(recent_requests)
        
        return stats
    
    def get_metrics_timeseries(self, metric_name: str, minutes: int = 60) -> List[Dict]:
        """获取指标时间序列：返回指定时间范围内的指标数据
        
        参数:
            metric_name: 指标名称
            minutes: 时间范围（分钟）
        返回:
            指标数据列表
        """
        if metric_name not in self.metrics:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            m for m in self.metrics[metric_name]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
    
    def get_prediction_distribution(self) -> Dict:
        """获取预测分布：统计各类预测结果的频次
        
        返回:
            预测类别计数字典
        """
        if not self.metrics["predictions"]:
            return {}
        
        predictions = [m["value"] for m in self.metrics["predictions"]]
        
        # 分类任务：统计频次
        distribution = {}
        for pred in predictions:
            distribution[pred] = distribution.get(pred, 0) + 1
        
        return distribution
    
    def export_dashboard_data(self) -> Dict:
        """导出Dashboard数据：生成前端展示所需的数据结构
        
        返回:
            完整的Dashboard数据字典
        """
        return {
            "realtime": self.get_realtime_stats(),
            "alerts": self.alerts[-10:],  # 最近10条告警
            "latency_series": self.get_metrics_timeseries("latency", minutes=60),
            "prediction_distribution": self.get_prediction_distribution(),
            "generated_at": datetime.now().isoformat()
        }

# 监控装饰器：便捷地包装函数实现自动性能监控
def monitored(monitor: ModelPerformanceMonitor):
    """监控装饰器
    
    使用方式：
    @monitored(my_monitor)
    def my_function():
        ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                latency = (time.time() - start) * 1000
                monitor.record_request(latency, success=True, prediction=result)
                return result
            except Exception as e:
                latency = (time.time() - start) * 1000
                monitor.record_request(latency, success=False)
                raise
        return wrapper
    return decorator

if __name__ == "__main__":
    # 创建监控器实例
    monitor = ModelPerformanceMonitor()
    
    # 模拟请求
    import random
    
    print("=== 模型性能监控 ===\n")
    
    # 模拟50个请求，包含不同场景
    for i in range(50):
        # 模拟不同场景的概率分布
        scenario = random.random()
        
        if scenario < 0.7:  # 70%正常请求：低延迟
            latency = random.uniform(50, 150)
            monitor.record_request(latency, success=True, prediction=random.choice(["A", "B", "C"]))
        elif scenario < 0.9:  # 20%慢请求：高延迟
            latency = random.uniform(500, 2000)
            monitor.record_request(latency, success=True, prediction="A")
        else:  # 10%错误：失败请求
            latency = random.uniform(100, 300)
            monitor.record_request(latency, success=False)
        
        time.sleep(0.01)
    
    # 打印统计结果
    stats = monitor.get_realtime_stats()
    print("实时统计:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    print("\n预测分布:")
    dist = monitor.get_prediction_distribution()
    print(json.dumps(dist, ensure_ascii=False, indent=2))
    
    print("\n告警记录:")
    for alert in monitor.alerts:
        print(f"[{alert['severity'].upper()}] {alert['message']}")
