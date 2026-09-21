"""
Tool日志系统
实现工具调用的完整日志记录和分析
"""

# 导入所需模块
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict  # 数据类
from datetime import datetime, timedelta  # 日期时间
from enum import Enum  # 枚举
import json  # JSON处理
import time  # 时间处理

class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ToolCallLog:
    """工具调用日志条目数据类"""
    log_id: str                        # 日志ID：唯一标识
    timestamp: datetime                # 调用时间
    user_id: str                       # 调用者ID
    tool_name: str                     # 工具名称
    params: Dict[str, Any]             # 调用参数
    result: Any                        # 执行结果
    success: bool                      # 是否成功
    duration_ms: float                 # 执行耗时（毫秒）
    level: LogLevel                    # 日志级别
    error_message: str = ""            # 错误信息（失败时）
    trace_id: str = ""                 # 分布式追踪ID


class ToolLogger:
    """工具日志记录器类 - 完整的日志管理解决方案"""
    
    def __init__(self, max_logs: int = 10000):
        """
        初始化日志记录器
        
        参数:
            max_logs: 最大保留日志条数（防止内存溢出）
        """
        self.logs: List[ToolCallLog] = []  # 日志列表
        self.max_logs = max_logs  # 最大日志数
        self.log_counter = 0  # 日志计数器（用于生成ID）
    
    def log(self, log_entry: ToolCallLog):
        """
        记录单条日志
        
        参数:
            log_entry: 日志条目对象
        """
        self.logs.append(log_entry)
        
        # 超出限制时清理旧日志（保留最新的）
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
    
    def create_log(
        self,
        user_id: str,
        tool_name: str,
        params: Dict,
        result: Any,
        success: bool,
        duration_ms: float,
        error_message: str = "",
        trace_id: str = ""
    ) -> ToolCallLog:
        """
        创建并记录日志条目的便捷方法
        
        参数:
            user_id: 用户ID
            tool_name: 工具名称
            params: 调用参数
            result: 执行结果
            success: 是否成功
            duration_ms: 执行耗时（毫秒）
            error_message: 错误信息
            trace_id: 追踪ID
        返回:
            创建的日志条目
        """
        self.log_counter += 1  # 计数器递增
        
        # 自动确定日志级别
        if not success:
            # 失败时使用ERROR级别
            level = LogLevel.ERROR
        elif duration_ms > 1000:  # 超过1秒认为是慢查询
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        # 创建日志条目
        log_entry = ToolCallLog(
            log_id=f"log_{self.log_counter}",  # 生成日志ID
            timestamp=datetime.now(),  # 当前时间
            user_id=user_id,
            tool_name=tool_name,
            params=params,
            result=result,
            success=success,
            duration_ms=duration_ms,
            level=level,
            error_message=error_message,
            trace_id=trace_id
        )
        
        self.log(log_entry)  # 记录日志
        return log_entry
    
    def query_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 100
    ) -> List[ToolCallLog]:
        """
        查询日志 - 支持多条件过滤
        
        参数:
            start_time: 开始时间过滤
            end_time: 结束时间过滤
            user_id: 用户ID过滤
            tool_name: 工具名称过滤
            success: 成功与否过滤
            limit: 返回条数限制
        返回:
            符合条件的日志列表（按时间倒序）
        """
        results = []
        
        # 倒序遍历（从新到旧）
        for log in reversed(self.logs):
            # 依次应用过滤条件
            if start_time and log.timestamp < start_time:
                continue
            if end_time and log.timestamp > end_time:
                continue
            if user_id and log.user_id != user_id:
                continue
            if tool_name and log.tool_name != tool_name:
                continue
            if success is not None and log.success != success:
                continue
            
            results.append(log)
            
            # 达到限制数量时停止
            if len(results) >= limit:
                break
        
        return results
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """
        获取统计信息 - 用于监控和分析
        
        参数:
            hours: 统计时间范围（小时）
        返回:
            统计结果字典
        """
        # 计算截止时间
        cutoff_time = datetime.now() - timedelta(hours=hours)
        # 筛选时间范围内的日志
        recent_logs = [log for log in self.logs if log.timestamp > cutoff_time]
        
        # 没有日志时返回空统计
        if not recent_logs:
            return {
                "period_hours": hours,
                "total_calls": 0,
                "success_rate": 0,
                "avg_duration_ms": 0
            }
        
        # 计算基础统计
        total = len(recent_logs)
        success_count = sum(1 for log in recent_logs if log.success)
        avg_duration = sum(log.duration_ms for log in recent_logs) / total
        
        # 按工具统计
        tool_stats = {}
        for log in recent_logs:
            if log.tool_name not in tool_stats:
                tool_stats[log.tool_name] = {"count": 0, "errors": 0}
            tool_stats[log.tool_name]["count"] += 1
            if not log.success:
                tool_stats[log.tool_name]["errors"] += 1
        
        return {
            "period_hours": hours,
            "total_calls": total,
            "success_rate": success_count / total,
            "avg_duration_ms": round(avg_duration, 2),
            "tool_statistics": tool_stats
        }
    
    def export_logs(self, filepath: str, format: str = "json"):
        """
        导出日志到文件
        
        参数:
            filepath: 导出文件路径
            format: 导出格式（json/csv）
        """
        if format == "json":
            # JSON格式导出
            data = [asdict(log) for log in self.logs]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        elif format == "csv":
            # CSV格式导出
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if self.logs:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.logs[0]).keys())
                    writer.writeheader()
                    for log in self.logs:
                        writer.writerow(asdict(log))


# 使用示例
if __name__ == "__main__":
    # 创建日志记录器（最多保留1000条）
    logger = ToolLogger(max_logs=1000)
    
    # 模拟记录一些工具调用（10次）
    for i in range(10):
        success = i < 8  # 80%成功率
        logger.create_log(
            user_id=f"user_{i % 3}",  # 3个用户轮询
            tool_name=["calculator", "weather", "search"][i % 3],  # 3个工具轮询
            params={"query": f"test_{i}"},
            result={"data": f"result_{i}"} if success else None,
            success=success,
            duration_ms=50 + i * 10,  # 耗时递增
            error_message="" if success else "模拟错误"
        )
    
    # 查询特定用户的日志
    print("=== 日志查询 ===")
    logs = logger.query_logs(user_id="user_0", limit=5)
    for log in logs:
        print(f"[{log.timestamp}] {log.user_id} -> {log.tool_name}: {'成功' if log.success else '失败'}")
    
    # 获取统计信息
    print("\n=== 统计信息 ===")
    stats = logger.get_statistics(hours=24)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
