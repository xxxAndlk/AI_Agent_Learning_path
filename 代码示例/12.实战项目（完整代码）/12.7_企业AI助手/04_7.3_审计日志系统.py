import json

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        self.logs: List[AuditLog] = []
        self.max_logs = 10000  # 最大保留日志数
    
    def log(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict,
        ip_address: str = "",
        user_agent: str = ""
    ):
        """记录审计日志"""
        log_id = str(uuid.uuid4())
        
        audit_log = AuditLog(
            log_id=log_id,
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.logs.append(audit_log)
        
        # 保持日志数量在限制内
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # 记录到文件
        logger.info(
            f"AUDIT: user={user_id} action={action} resource={resource}"
        )
    
    def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """查询审计日志"""
        results = self.logs
        
        if user_id:
            results = [log for log in results if log.user_id == user_id]
        
        if action:
            results = [log for log in results if log.action == action]
        
        if start_time:
            results = [log for log in results if log.timestamp >= start_time]
        
        if end_time:
            results = [log for log in results if log.timestamp <= end_time]
        
        # 按时间倒序
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        
        return [log.to_dict() for log in results[:limit]]
    
    def get_user_activity(self, user_id: str, days: int = 7) -> Dict:
        """获取用户活动统计"""
        from datetime import timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        user_logs = [
            log for log in self.logs
            if log.user_id == user_id and log.timestamp >= start_date
        ]
        
        # 统计操作类型
        action_counts = {}
        for log in user_logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_actions": len(user_logs),
            "action_breakdown": action_counts,
            "first_activity": user_logs[-1].timestamp if user_logs else None,
            "last_activity": user_logs[0].timestamp if user_logs else None
        }
    
    def export_logs(self, format: str = "json") -> str:
        """导出日志"""
        if format == "json":
            return json.dumps(
                [log.to_dict() for log in self.logs],
                indent=2,
                ensure_ascii=False
            )
        elif format == "csv":
            # 简单的CSV导出
            lines = ["log_id,user_id,action,resource,timestamp"]
            for log in self.logs:
                lines.append(
                    f"{log.log_id},{log.user_id},{log.action},"
                    f"{log.resource},{log.timestamp.isoformat()}"
                )
            return "\n".join(lines)
        
        return str(self.logs)


# 使用审计日志
audit_logger = AuditLogger()
audit_logger.log(
    user_id="emp001",
    action="chat",
    resource="ai_assistant",
    details={"query": "年假政策", "intent": "knowledge_query"}
)
print("审计日志记录完成")
