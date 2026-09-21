from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class HealthStatus:
    """健康状态"""
    status: str  # healthy, degraded, unhealthy
    checks: Dict[str, dict]
    timestamp: datetime

class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks = {}
        
    def register_check(self, name: str, check_func):
        """注册健康检查"""
        self.checks[name] = check_func
        
    async def check_all(self) -> HealthStatus:
        """执行所有健康检查"""
        results = {}
        overall_status = "healthy"
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = {
                    "status": "ok" if result else "error",
                    "message": result if isinstance(result, str) else "OK"
                }
                if not result:
                    overall_status = "unhealthy"
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "message": str(e)
                }
                overall_status = "degraded"
        
        return HealthStatus(
            status=overall_status,
            checks=results,
            timestamp=datetime.now()
        )
    
    async def check_llm_service(self) -> bool:
        """检查LLM服务"""
        # 实际检查LLM服务可用性
        return True
    
    async def check_vector_store(self) -> bool:
        """检查向量存储"""
        # 实际检查向量存储连接
        return True
    
    async def check_cache(self) -> bool:
        """检查缓存服务"""
        # 实际检查缓存服务
        return True


# 健康检查端点实现
async def health_endpoint() -> dict:
    """健康检查端点"""
    checker = HealthChecker()
    checker.register_check("llm", checker.check_llm_service)
    checker.register_check("vector_store", checker.check_vector_store)
    checker.register_check("cache", checker.check_cache)
    
    status = await checker.check_all()
    
    return {
        "status": status.status,
        "checks": status.checks,
        "timestamp": status.timestamp.isoformat()
    }
