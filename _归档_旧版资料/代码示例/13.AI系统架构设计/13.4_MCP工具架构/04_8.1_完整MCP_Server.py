"""
完整的MCP Server实现
支持多种通信模式和工具注册
"""

import json
import asyncio
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPToolBase(ABC):
    """MCP工具基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict:
        """获取工具Schema"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        pass


class FileTool(MCPToolBase):
    """文件操作工具"""
    
    @property
    def name(self) -> str:
        return "file"
    
    @property
    def description(self) -> str:
        return "读取、写入、删除和列出文件"
    
    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "delete", "list"],
                        "description": "操作类型"
                    },
                    "path": {
                        "type": "string",
                        "description": "文件路径"
                    },
                    "content": {
                        "type": "string",
                        "description": "写入内容（write操作时需要）"
                    }
                },
                "required": ["operation", "path"]
            }
        }
    
    def execute(self, operation: str, path: str, content: str = "") -> Any:
        """执行文件操作"""
        import os
        
        if operation == "read":
            if not os.path.exists(path):
                return {"error": f"文件不存在: {path}"}
            with open(path, "r", encoding="utf-8") as f:
                return {"content": f.read()}
        
        elif operation == "write":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "path": path}
        
        elif operation == "delete":
            if os.path.exists(path):
                os.remove(path)
                return {"success": True}
            return {"error": f"文件不存在: {path}"}
        
        elif operation == "list":
            if not os.path.exists(path):
                return {"error": f"目录不存在: {path}"}
            files = os.listdir(path)
            return {"files": files, "path": path}
        
        return {"error": f"未知操作: {operation}"}


class HTTPRequestTool(MCPToolBase):
    """HTTP请求工具"""
    
    @property
    def name(self) -> str:
        return "http"
    
    @property
    def description(self) -> str:
        return "发送HTTP请求"
    
    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
                    },
                    "url": {"type": "string"},
                    "headers": {"type": "object"},
                    "body": {"type": "object"}
                },
                "required": ["method", "url"]
            }
        }
    
    async def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        body: Optional[Dict] = None
    ) -> Any:
        """执行HTTP请求"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers or {},
                json=body
            ) as response:
                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": await response.text()
                }


class CalculatorTool(MCPToolBase):
    """计算器工具"""
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "执行数学计算"
    
    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 2+2, sqrt(16), sin(0)"
                    }
                },
                "required": ["expression"]
            }
        }
    
    def execute(self, expression: str) -> Any:
        """执行计算"""
        try:
            # 注意：实际使用应该使用安全的计算器库
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "sqrt": lambda x: x**0.5
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"error": str(e)}


class MCPServer:
    """MCP服务器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPToolBase] = {}
        self.capabilities: Dict = {}
        self.request_handlers: Dict[str, Callable] = {}
        
        # 注册默认处理器
        self._register_default_handlers()
        
        # 注册默认工具
        self._register_default_tools()
    
    def _register_default_handlers(self):
        """注册默认请求处理器"""
        self.request_handlers = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "ping": self._handle_ping
        }
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool(FileTool())
        self.register_tool(HTTPRequestTool())
        self.register_tool(CalculatorTool())
    
    def register_tool(self, tool: MCPToolBase):
        """注册工具"""
        self.tools[tool.name] = tool
        logger.info(f"工具已注册: {tool.name}")
    
    def unregister_tool(self, tool_name: str):
        """注销工具"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"工具已注销: {tool_name}")
    
    def _handle_initialize(self, params: Dict) -> Dict:
        """处理初始化请求"""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "enterprise-mcp-server",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            }
        }
    
    def _handle_tools_list(self, params: Dict) -> Dict:
        """处理工具列表请求"""
        return {
            "tools": [tool.get_schema() for tool in self.tools.values()]
        }
    
    def _handle_tools_call(self, params: Dict) -> Dict:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "error": {
                    "code": -32601,
                    "message": f"未知工具: {tool_name}"
                }
            }
        
        tool = self.tools[tool_name]
        
        try:
            # 判断是否异步执行
            import asyncio
            if asyncio.iscoroutinefunction(tool.execute):
                result = asyncio.run(tool.execute(**arguments))
            else:
                result = tool.execute(**arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False)
                    }
                ]
            }
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"工具执行错误: {str(e)}"
                }
            }
    
    def _handle_ping(self, params: Dict) -> Dict:
        """处理ping请求"""
        return {"status": "ok"}
    
    def handle_request(self, request: Dict) -> Dict:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"处理请求: {method}")
        
        handler = self.request_handlers.get(method)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"未知方法: {method}"
                }
            }
        
        try:
            result = handler(params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"处理请求出错: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def process_json(self, json_str: str) -> str:
        """处理JSON请求"""
        try:
            request = json.loads(json_str)
            response = self.handle_request(request)
            return json.dumps(response, ensure_ascii=False)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"JSON解析错误: {str(e)}"
                }
            }
            return json.dumps(error_response, ensure_ascii=False)


# 运行Server
if __name__ == "__main__":
    server = MCPServer()
    
    # 测试请求
    test_requests = [
        {"method": "tools/list", "params": {}, "id": "1"},
        {"method": "tools/call", "params": {
            "name": "calculator",
            "arguments": {"expression": "2+2"}
        }, "id": "2"},
        {"method": "tools/call", "params": {
            "name": "file",
            "arguments": {"operation": "list", "path": "."}
        }, "id": "3"}
    ]
    
    for req in test_requests:
        response = server.handle_request(req)
        print(f"\n请求: {req['method']}")
        print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
