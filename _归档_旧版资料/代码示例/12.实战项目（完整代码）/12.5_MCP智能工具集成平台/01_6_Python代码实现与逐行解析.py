"""
MCP智能工具集成平台
实现一个支持多工具集成的MCP Server
统一管理数据库、GitHub、Slack等多种工具
"""

import json
import sys
import subprocess
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
import sqlite3

# ============ 数据库工具 ============

class DatabaseTool:
    """数据库工具：提供SQL查询和执行功能"""
    
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self._init_db()  # 初始化数据库结构
    
    def _init_db(self):
        """初始化数据库：创建表并插入示例数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建示例表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入示例数据（如果表为空）
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                [
                    ("张三", "zhangsan@example.com"),
                    ("李四", "lisi@example.com"),
                    ("王五", "wangwu@example.com")
                ]
            )
        
        conn.commit()
        conn.close()
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """执行查询：返回查询结果
        
        参数:
            sql: SQL查询语句
            params: 查询参数元组
        返回:
            查询结果列表（字典格式）
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def execute(self, sql: str, params: tuple = ()) -> int:
        """执行SQL：执行INSERT/UPDATE/DELETE语句
        
        参数:
            sql: SQL语句
            params: 执行参数
        返回:
            受影响的行数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

# ============ GitHub工具 ============

class GitHubTool:
    """GitHub工具（模拟）：提供仓库和Issue操作功能"""
    
    def __init__(self, token: str = ""):
        self.token = token
    
    def get_repo_info(self, owner: str, repo: str) -> Dict:
        """获取仓库信息
        
        参数:
            owner: 仓库所有者
            repo: 仓库名称
        返回:
            仓库信息字典
        """
        # 模拟GitHub API响应
        return {
            "name": repo,
            "owner": owner,
            "stars": 1500,
            "forks": 300,
            "open_issues": 45,
            "language": "Python",
            "description": f"这是一个由{owner}维护的优秀项目"
        }
    
    def list_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """列出问题
        
        参数:
            owner: 仓库所有者
            repo: 仓库名称
            state: Issue状态（open/closed）
        返回:
            Issue列表
        """
        return [
            {"number": i+1, "title": f"问题{i+1}", "state": state, "created_at": "2024-01-01"}
            for i in range(5)
        ]
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> Dict:
        """创建问题
        
        参数:
            owner: 仓库所有者
            repo: 仓库名称
            title: Issue标题
            body: Issue内容
        返回:
            创建的Issue信息
        """
        return {
            "number": 100,
            "title": title,
            "state": "open",
            "created_at": datetime.now().isoformat()
        }

# ============ Slack工具 ============

class SlackTool:
    """Slack工具（模拟）：提供消息发送和频道管理功能"""
    
    def __init__(self, token: str = ""):
        self.token = token
    
    def send_message(self, channel: str, text: str) -> Dict:
        """发送消息
        
        参数:
            channel: 频道名称
            text: 消息内容
        返回:
            发送结果
        """
        return {
            "ok": True,
            "channel": channel,
            "ts": datetime.now().timestamp(),
            "text": text
        }
    
    def get_channels(self) -> List[Dict]:
        """获取频道列表
        
        返回:
            频道信息列表
        """
        return [
            {"id": "C001", "name": "general", "is_archived": False},
            {"id": "C002", "name": "random", "is_archived": False},
            {"id": "C003", "name": "development", "is_archived": False}
        ]

# ============ MCP Server实现 ============

class MCPToolsPlatform:
    """MCP工具平台：管理所有工具的注册和调用"""
    
    def __init__(self):
        """初始化平台"""
        self.tools: Dict[str, Any] = {}            # 工具实例存储
        self.tool_schemas: Dict[str, Dict] = {}   # 工具Schema存储
        self.call_history: List[Dict] = []         # 调用历史
        self._register_tools()                      # 注册所有工具
    
    def _register_tools(self):
        """注册所有工具：为每个工具创建实例并定义Schema"""
        # 数据库工具
        db = DatabaseTool()
        self.tools["database"] = db
        self.tool_schemas["database"] = {
            "name": "database",
            "description": "数据库查询和操作工具",
            "methods": {
                "query": {
                    "description": "执行SQL查询",
                    "parameters": {
                        "sql": {"type": "string", "description": "SQL语句"},
                        "params": {"type": "array", "description": "查询参数"}
                    }
                },
                "execute": {
                    "description": "执行SQL（INSERT/UPDATE/DELETE）",
                    "parameters": {
                        "sql": {"type": "string", "description": "SQL语句"},
                        "params": {"type": "array", "description": "执行参数"}
                    }
                }
            }
        }
        
        # GitHub工具
        github = GitHubTool()
        self.tools["github"] = github
        self.tool_schemas["github"] = {
            "name": "github",
            "description": "GitHub API工具",
            "methods": {
                "get_repo_info": {
                    "description": "获取仓库信息",
                    "parameters": {
                        "owner": {"type": "string", "description": "仓库所有者"},
                        "repo": {"type": "string", "description": "仓库名"}
                    }
                },
                "list_issues": {
                    "description": "列出问题",
                    "parameters": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "state": {"type": "string", "enum": ["open", "closed", "all"]}
                    }
                },
                "create_issue": {
                    "description": "创建问题",
                    "parameters": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "title": {"type": "string"},
                        "body": {"type": "string"}
                    }
                }
            }
        }
        
        # Slack工具
        slack = SlackTool()
        self.tools["slack"] = slack
        self.tool_schemas["slack"] = {
            "name": "slack",
            "description": "Slack消息工具",
            "methods": {
                "send_message": {
                    "description": "发送消息到频道",
                    "parameters": {
                        "channel": {"type": "string", "description": "频道名"},
                        "text": {"type": "string", "description": "消息内容"}
                    }
                },
                "get_channels": {
                    "description": "获取频道列表",
                    "parameters": {}
                }
            }
        }
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具：返回平台注册的所有工具信息"""
        return [
            {
                "name": name,
                "description": schema["description"],
                "methods": list(schema["methods"].keys())
            }
            for name, schema in self.tool_schemas.items()
        ]
    
    def call_tool(self, tool_name: str, method: str, params: Dict) -> Dict:
        """调用工具：执行指定的工具方法
        
        参数:
            tool_name: 工具名称
            method: 方法名称
            params: 方法参数
        返回:
            调用结果字典
        """
        if tool_name not in self.tools:
            return {"error": f"未知工具: {tool_name}"}
        
        tool = self.tools[tool_name]
        
        if not hasattr(tool, method):
            return {"error": f"工具'{tool_name}'没有方法'{method}'"}
        
        try:
            # 记录调用
            call_record = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "method": method,
                "params": params
            }
            
            # 执行调用
            method_func = getattr(tool, method)
            result = method_func(**params)
            
            # 记录结果
            call_record["success"] = True
            call_record["result"] = result
            self.call_history.append(call_record)
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            call_record["success"] = False
            call_record["error"] = str(e)
            self.call_history.append(call_record)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_call_history(self, limit: int = 100) -> List[Dict]:
        """获取调用历史
        
        参数:
            limit: 返回记录数量限制
        返回:
            调用历史列表
        """
        return self.call_history[-limit:]

# ============ MCP协议适配器 ============

class MCPServerAdapter:
    """MCP Server适配器：处理MCP协议格式的请求"""
    
    def __init__(self, platform: MCPToolsPlatform):
        """初始化适配器
        
        参数:
            platform: MCP工具平台实例
        """
        self.platform = platform
    
    def handle_request(self, request: Dict) -> Dict:
        """处理MCP请求：解析并路由MCP协议请求
        
        参数:
            request: MCP协议格式的请求
        返回:
            MCP协议格式的响应
        """
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")
        
        result = None
        
        # initialize：初始化连接
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "mcp-tools-platform", "version": "1.0.0"},
                "capabilities": {"tools": {}}
            }
        
        # tools/list：列出所有工具
        elif method == "tools/list":
            tools = self.platform.list_tools()
            result = {"tools": tools}
        
        # tools/call：调用工具方法
        elif method == "tools/call":
            tool_name = params.get("tool")
            method_name = params.get("method")
            arguments = params.get("arguments", {})
            
            call_result = self.platform.call_tool(tool_name, method_name, arguments)
            result = call_result
        
        # tools/history：获取调用历史
        elif method == "tools/history":
            limit = params.get("limit", 100)
            result = {"history": self.platform.get_call_history(limit)}
        
        # 返回响应
        if result is not None and req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        
        return {"error": "Unknown method"}

# 使用示例
if __name__ == "__main__":
    # 创建平台
    platform = MCPToolsPlatform()
    
    # 列出所有工具
    print("可用工具:")
    for tool in platform.list_tools():
        print(f"\n  📦 {tool['name']}: {tool['description']}")
        print(f"     方法: {', '.join(tool['methods'])}")
    
    # 测试数据库工具
    print("\n--- 数据库查询 ---")
    result = platform.call_tool("database", "query", {"sql": "SELECT * FROM users LIMIT 3", "params": []})
    print(f"查询结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试GitHub工具
    print("\n--- GitHub查询 ---")
    result = platform.call_tool("github", "get_repo_info", {"owner": "octocat", "repo": "Hello-World"})
    print(f"仓库信息: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试Slack工具
    print("\n--- Slack发送 ---")
    result = platform.call_tool("slack", "send_message", {"channel": "general", "text": "Hello from MCP!"})
    print(f"发送结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 查看调用历史
    print("\n--- 调用历史 ---")
    history = platform.get_call_history(limit=10)
    for record in history:
        status = "✅" if record["success"] else "❌"
        print(f"  {status} [{record['timestamp']}] {record['tool']}.{record['method']}")
