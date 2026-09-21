"""
MCP协议消息格式详解

MCP协议使用JSON格式进行消息传递，消息分为：
1. 请求消息 (Request)
2. 响应消息 (Response)
3. 通知消息 (Notification)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid


class MCPMethod(str, Enum):
    """MCP方法枚举"""
    # 初始化
    INITIALIZE = "initialize"
    
    # 工具相关
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    # 资源相关
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    RESOURCES_SUBSCRIBE = "resources/subscribe"
    
    # 提示相关
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"


@dataclass
class MCPRequest:
    """MCP请求消息"""
    jsonrpc: str = "2.0"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params
        }, ensure_ascii=False)


@dataclass
class MCPResponse:
    """MCP响应消息"""
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        data = {"jsonrpc": self.jsonrpc, "id": self.id}
        
        if self.error:
            data["error"] = self.error
        else:
            data["result"] = self.result
        
        return json.dumps(data, ensure_ascii=False)
    
    @staticmethod
    def from_json(json_str: str) -> "MCPResponse":
        data = json.loads(json_str)
        return MCPResponse(
            id=data.get("id", ""),
            result=data.get("result"),
            error=data.get("error")
        )


@dataclass
class MCPNotification:
    """MCP通知消息（无响应）"""
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        return json.dumps({
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params
        }, ensure_ascii=False)


# 协议版本
PROTOCOL_VERSION = "2024-11-05"


class MCPProtocol:
    """MCP协议处理器"""
    
    @staticmethod
    def create_initialize_request() -> MCPRequest:
        """创建初始化请求"""
        return MCPRequest(
            method=MCPMethod.INITIALIZE.value,
            params={
                "protocolVersion": PROTOCOL_VERSION,
                "clientInfo": {
                    "name": "mcp-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                }
            }
        )
    
    @staticmethod
    def create_tools_list_request() -> MCPRequest:
        """创建工具列表请求"""
        return MCPRequest(method=MCPMethod.TOOLS_LIST.value)
    
    @staticmethod
    def create_tool_call_request(
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> MCPRequest:
        """创建工具调用请求"""
        return MCPRequest(
            method=MCPMethod.TOOLS_CALL.value,
            params={
                "name": tool_name,
                "arguments": arguments
            }
        )
    
    @staticmethod
    def parse_response(response_json: str) -> MCPResponse:
        """解析响应"""
        return MCPResponse.from_json(response_json)
