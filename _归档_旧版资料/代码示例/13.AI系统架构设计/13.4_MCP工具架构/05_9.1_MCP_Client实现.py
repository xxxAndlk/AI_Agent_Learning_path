"""
MCP Client实现 - 用于连接MCP Server并调用工具
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import aiohttp
import uuid


@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    description: str
    parameters: Dict


@dataclass
class ToolCallResult:
    """工具调用结果"""
    success: bool
    result: Any
    error: Optional[str] = None


class MCPClient:
    """MCP客户端"""
    
    def __init__(
        self,
        server_url: str = None,
        transport: str = "http"
    ):
        """
        初始化MCP客户端
        
        参数:
            server_url: 服务器URL（HTTP模式）
            transport: 传输模式：http, websocket, stdio
        """
        self.server_url = server_url
        self.transport = transport
        
        self.tools: Dict[str, ToolInfo] = {}
        self.protocol_version: str = ""
        self.server_info: Dict = {}
        self.session_id: str = str(uuid.uuid4())
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """初始化连接"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "mcp-client-python",
                    "version": "1.0.0"
                },
                "capabilities": {}
            }
        }
        
        response = await self._send_request(request)
        
        if "result" in response:
            result = response["result"]
            self.protocol_version = result.get("protocolVersion", "")
            self.server_info = result.get("serverInfo", {})
            self._initialized = True
            
            # 获取工具列表
            await self.list_tools()
            
            return True
        
        return False
    
    async def list_tools(self) -> List[ToolInfo]:
        """获取工具列表"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_request(request)
        
        self.tools = {}
        if "result" in response:
            tools_data = response["result"].get("tools", [])
            for tool_data in tools_data:
                self.tools[tool_data["name"]] = ToolInfo(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    parameters=tool_data.get("parameters", {})
                )
        
        return list(self.tools.values())
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ToolCallResult:
        """调用工具"""
        if not self._initialized:
            await self.initialize()
        
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "result" in response:
            result = response["result"]
            content = result.get("content", [])
            if content:
                text = content[0].get("text", "{}")
                try:
                    return ToolCallResult(
                        success=True,
                        result=json.loads(text)
                    )
                except:
                    return ToolCallResult(
                        success=True,
                        result=text
                    )
        
        if "error" in response:
            return ToolCallResult(
                success=False,
                result=None,
                error=response["error"].get("message", "Unknown error")
            )
        
        return ToolCallResult(
            success=False,
            result=None,
            error="Unknown error"
        )
    
    async def _send_request(self, request: Dict) -> Dict:
        """发送请求"""
        if self.transport == "http" and self.server_url:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.server_url,
                    json=request,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    return await resp.json()
        
        # 简化的内存实现（用于测试）
        return {"jsonrpc": "2.0", "id": request.get("id"), "result": {}}
    
    def get_tool_schema(self, tool_name: str) -> Optional[ToolInfo]:
        """获取工具Schema"""
        return self.tools.get(tool_name)
    
    def list_tool_names(self) -> List[str]:
        """列出所有工具名称"""
        return list(self.tools.keys())


class MCPClientDemo:
    """演示客户端用法"""
    
    @staticmethod
    async def demo():
        """演示"""
        print("MCP客户端演示")
        print("=" * 50)
        
        # 注意：这里使用内存模拟，实际应连接真实服务器
        # client = MCPClient(server_url="http://localhost:8000/mcp")
        
        # 创建本地Server进行演示
        from main import MCPServer
        server = MCPServer()
        
        # 模拟客户端请求
        # 1. 列出工具
        request = {"method": "tools/list", "params": {}, "id": "1"}
        response = server.handle_request(request)
        print("工具列表:")
        if "result" in response:
            tools = response["result"].get("tools", [])
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        
        # 2. 调用计算器工具
        request = {
            "method": "tools/call",
            "params": {
                "name": "calculator",
                "arguments": {"expression": "10 * 5 + 3"}
            },
            "id": "2"
        }
        response = server.handle_request(request)
        print("\n计算结果:")
        if "result" in response:
            print(f"  {response['result']}")
        
        # 3. 调用文件工具
        request = {
            "method": "tools/call",
            "params": {
                "name": "file",
                "arguments": {"operation": "read", "path": "test.txt"}
            },
            "id": "3"
        }
        response = server.handle_request(request)
        print("\n文件读取结果:")
        print(f"  {response}")


if __name__ == "__main__":
    asyncio.run(MCPClientDemo.demo())
