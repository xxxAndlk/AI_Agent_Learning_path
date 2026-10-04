"""
MCP工具架构

MCP通信模式：
- stdio: 标准输入输出，适合本地工具
- Streamable HTTP: 远程服务（取代早期HTTP/SSE）
- WebSocket: 双向通信
"""

from typing import Dict, List, Any, Optional
import json
import sqlite3
from datetime import datetime


class MCPTool:
    """MCP工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def get_schema(self) -> Dict:
        """获取工具Schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {}
        }
    
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        raise NotImplementedError


class DatabaseTool(MCPTool):
    """数据库工具"""
    
    def __init__(self, db_path: str = "data.db"):
        super().__init__("database", "数据库查询和操作工具")
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')
        conn.commit()
        conn.close()
    
    def execute(self, operation: str, sql: str = "", params: tuple = ()) -> Any:
        """执行数据库操作"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if operation == "query":
                cursor.execute(sql, params)
                return cursor.fetchall()
            elif operation == "execute":
                cursor.execute(sql, params)
                conn.commit()
                return {"rows_affected": cursor.rowcount}
        finally:
            conn.close()
    
    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "methods": {
                "query": {"description": "执行SQL查询", "params": ["sql", "params"]},
                "execute": {"description": "执行SQL", "params": ["sql", "params"]}
            }
        }


class MCPServer:
    """MCP服务器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        db_tool = DatabaseTool()
        self.tools["database"] = db_tool
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [tool.get_schema() for tool in self.tools.values()]
    
    def call_tool(self, tool_name: str, method: str, params: Dict) -> Dict:
        """调用工具"""
        if tool_name not in self.tools:
            return {"error": f"未知工具: {tool_name}"}
        
        tool = self.tools[tool_name]
        
        try:
            result = tool.execute(**params)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_request(self, request: Dict) -> Dict:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "mcp-server", "version": "1.0.0"},
                "capabilities": {"tools": {}}
            }
        elif method == "tools/list":
            return {"tools": self.list_tools()}
        elif method == "tools/call":
            return self.call_tool(
                params.get("tool"),
                params.get("method"),
                params.get("arguments", {})
            )
        
        return {"error": "Unknown method"}


def main():
    """主函数"""
    # 创建MCP服务器
    server = MCPServer()
    
    # 处理请求
    request = {"method": "tools/list", "params": {}}
    response = server.handle_request(request)
    print("工具列表:", json.dumps(response, indent=2, ensure_ascii=False))
    
    # 调用工具
    request = {
        "method": "tools/call",
        "params": {
            "tool": "database",
            "method": "query",
            "arguments": {"sql": "SELECT * FROM users LIMIT 3"}
        }
    }
    response = server.handle_request(request)
    print("\n查询结果:", json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
