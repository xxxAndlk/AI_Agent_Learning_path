"""
AI SaaS架构

多租户策略：
- 数据库隔离：独立数据库，成本最高，安全性最高
- Schema隔离：独立Schema，成本中等
- 租户ID：行级隔离，成本最低
"""

from typing import Dict, List, Optional
from datetime import datetime
import time


class TenantManager:
    """租户管理器"""
    
    def __init__(self):
        # 租户信息存储
        self.tenants: Dict[str, Dict] = {}
        
        # API密钥到租户ID的映射
        self.api_key_to_tenant: Dict[str, str] = {}
        
        # 配额使用记录
        self.usage_records: Dict[str, Dict] = {}
    
    def create_tenant(
        self,
        name: str,
        plan: str = "free",
        quota: Dict = None
    ) -> str:
        """创建租户"""
        tenant_id = f"tenant_{int(time.time())}"
        
        # 默认配额
        default_quota = {
            "free": {"requests_per_day": 100, "storage_mb": 100},
            "pro": {"requests_per_day": 10000, "storage_mb": 10000},
            "enterprise": {"requests_per_day": -1, "storage_mb": -1}
        }
        
        self.tenants[tenant_id] = {
            "id": tenant_id,
            "name": name,
            "plan": plan,
            "quota": quota or default_quota.get(plan, {}),
            "created_at": datetime.now().isoformat()
        }
        
        # 生成API密钥
        api_key = f"sk_{tenant_id}_{int(time.time())}"
        self.api_key_to_tenant[api_key] = tenant_id
        
        # 初始化使用记录
        self.usage_records[tenant_id] = {
            "requests_today": 0,
            "last_reset": datetime.now().date(),
            "total_requests": 0,
            "total_tokens": 0
        }
        
        return tenant_id
    
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Dict]:
        """通过API密钥获取租户"""
        tenant_id = self.api_key_to_tenant.get(api_key)
        if tenant_id:
            return self.tenants.get(tenant_id)
        return None
    
    def check_quota(self, tenant_id: str, requested: int = 1) -> bool:
        """检查配额"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        usage = self.usage_records.get(tenant_id, {})
        
        # 检查每日限制
        quota = tenant.get("quota", {})
        daily_limit = quota.get("requests_per_day", -1)
        
        if daily_limit > 0:
            if usage.get("requests_today", 0) + requested > daily_limit:
                return False
        
        return True
    
    def record_usage(self, tenant_id: str, tokens: int = 0):
        """记录使用量"""
        if tenant_id not in self.usage_records:
            self.usage_records[tenant_id] = {
                "requests_today": 0,
                "last_reset": datetime.now().date(),
                "total_requests": 0,
                "total_tokens": 0
            }
        
        usage = self.usage_records[tenant_id]
        
        # 检查是否需要重置每日计数
        today = datetime.now().date()
        if usage["last_reset"] != today:
            usage["requests_today"] = 0
            usage["last_reset"] = today
        
        usage["requests_today"] += 1
        usage["total_requests"] += 1
        usage["total_tokens"] += tokens
    
    def get_usage_summary(self, tenant_id: str) -> Dict:
        """获取使用摘要"""
        return self.usage_records.get(tenant_id, {})


class AISaaSService:
    """AI SaaS服务"""
    
    def __init__(self):
        self.tenant_manager = TenantManager()
    
    def verify_request(self, api_key: str) -> Optional[Dict]:
        """验证请求"""
        tenant = self.tenant_manager.get_tenant_by_api_key(api_key)
        if not tenant:
            raise ValueError("无效的API密钥")
        
        if not self.tenant_manager.check_quota(tenant["id"]):
            raise ValueError("超出配额限制")
        
        return tenant
    
    def process_request(
        self,
        api_key: str,
        prompt: str,
        model: str = "gpt-5.4-mini",
        **kwargs
    ) -> Dict:
        """处理AI请求"""
        # 验证请求
        tenant = self.verify_request(api_key)
        
        # 模拟LLM调用
        response = f"处理请求: {prompt[:50]}..."
        
        # 估算token消耗
        tokens_used = len(prompt) // 4 + len(response) // 4
        
        # 记录使用量
        self.tenant_manager.record_usage(tenant["id"], tokens_used)
        
        return {
            "response": response,
            "model": model,
            "tokens_used": tokens_used,
            "tenant_id": tenant["id"]
        }


def main():
    """主函数"""
    # 创建SaaS服务
    service = AISaaSService()
    
    # 创建租户
    tenant_id = service.tenant_manager.create_tenant(
        name="示例公司",
        plan="pro"
    )
    
    print(f"创建租户: {tenant_id}")
    
    # 获取API密钥（实际应返回给租户）
    api_key = None
    for key, tid in service.tenant_manager.api_key_to_tenant.items():
        if tid == tenant_id:
            api_key = key
            break
    
    print(f"API密钥: {api_key}")
    
    # 处理请求
    response = service.process_request(
        api_key=api_key,
        prompt="帮我写一首诗"
    )
    
    print(f"响应: {response}")
    
    # 查看使用量
    usage = service.tenant_manager.get_usage_summary(tenant_id)
    print(f"使用量: {usage}")


if __name__ == "__main__":
    main()
