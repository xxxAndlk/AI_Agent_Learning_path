"""
完整的MCP系统示例
包含Server、Client、工具注册和安全认证
"""

import asyncio
from typing import Dict, Any
import json


class EnterpriseMCPSystem:
    """企业级MCP系统"""
    
    def __init__(self):
        # 初始化各组件
        self.server = MCPServer()
        self.registry = ToolRegistry()
        self.auth = MCPAuthenticator(secret_key="enterprise-secret-key")
        
        # 注册工具
        self._setup_tools()
        
        # 设置权限
        self._setup_permissions()
    
    def _setup_tools(self):
        """设置工具"""
        # 注册已实现的工具
        self.registry.register(
            FileTool(),
            version="1.0.0",
            author="System",
            tags=["file", "io"]
        )
        
        self.registry.register(
            CalculatorTool(),
            version="1.0.0",
            author="System",
            tags=["utility", "math"]
        )
        
        self.registry.register(
            HTTPRequestTool(),
            version="1.0.0",
            author="System",
            tags=["http", "network"]
        )
        
        # 添加自定义工具
        self._add_custom_tools()
    
    def _add_custom_tools(self):
        """添加自定义工具"""
        
        class CustomDBTool(MCPToolBase):
            @property
            def name(self): return "custom_db"
            
            @property
            def description(self): return "自定义数据库工具"
            
            def get_schema(self):
                return {
                    "name": self.name,
                    "description": self.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        }
                    }
                }
            
            def execute(self, query: str):
                return {"result": "模拟数据库查询结果", "query": query}
        
        self.registry.register(
            CustomDBTool(),
            version="1.0.0",
            author="CustomTeam",
            tags=["database", "custom"]
        )
    
    def _setup_permissions(self):
        """设置权限"""
        # 允许所有角色使用基础工具
        permission_manager = ToolPermission()
        permission_manager.allow("calculator", ["admin", "user", "guest"])
        permission_manager.allow("file", ["admin", "user"])
        permission_manager.allow("custom_db", ["admin"])
        
        self.permission_manager = permission_manager
    
    def process_request(
        self,
        request: Dict,
        auth_info: Dict = None
    ) -> Dict:
        """处理请求（含认证）"""
        method = request.get("method")
        
        # 工具调用需要认证
        if method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            
            # 检查权限
            if auth_info:
                user_roles = auth_info.get("roles", [])
                has_permission = False
                
                for role in user_roles:
                    if self.permission_manager.check_permission(tool_name, role):
                        has_permission = True
                        break
                
                if not has_permission:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32603,
                            "message": f"没有权限调用工具: {tool_name}"
                        }
                    }
        
        # 处理请求
        return self.server.handle_request(request)
    
    def get_system_info(self) -> Dict:
        """获取系统信息"""
        return {
            "server": self.server.server_info,
            "tools": self.registry.list_tools(),
            "api_key": self.auth.create_api_key("system", "系统密钥")
        }


def demo():
    """演示企业级MCP系统"""
    print("=" * 60)
    print("企业级MCP系统演示")
    print("=" * 60)
    
    # 创建系统
    system = EnterpriseMCPSystem()
    
    # 显示系统信息
    info = system.get_system_info()
    print(f"\n服务器信息: {info['server']}")
    print(f"生成的API密钥: {info['api_key'][:30]}...")
    
    # 测试工具调用
    print("\n" + "-" * 40)
    print("测试工具调用")
    print("-" * 40)
    
    # 1. 列出工具
    request = {"method": "tools/list", "params": {}, "id": "1"}
    response = system.server.handle_request(request)
    tools = response.get("result", {}).get("tools", [])
    print(f"\n可用工具数量: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # 2. 调用计算器
    request = {
        "method": "tools/call",
        "params": {
            "name": "calculator",
            "arguments": {"expression": "100 / 5 + 10"}
        },
        "id": "2"
    }
    response = system.server.handle_request(request)
    print(f"\n计算器调用: {response}")
    
    # 3. 调用数据库工具
    request = {
        "method": "tools/call",
        "params": {
            "name": "custom_db",
            "arguments": {"query": "SELECT * FROM users"}
        },
        "id": "3"
    }
    response = system.server.handle_request(request)
    print(f"数据库工具调用: {response}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
