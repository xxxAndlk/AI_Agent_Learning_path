import json
"""
工具Schema定义规范

Tool Schema用于描述工具的能力，使AI能够理解如何调用工具
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ParameterType(str, Enum):
    """参数类型"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    description: str
    type: ParameterType
    required: bool = False
    default: Any = None
    enum: Optional[List[str]] = None
    items: Optional[Dict] = None  # for array type
    
    def to_dict(self) -> Dict:
        result = {
            "type": self.type.value,
            "description": self.description
        }
        
        if self.required:
            result["required"] = self.required
        
        if self.default is not None:
            result["default"] = self.default
        
        if self.enum:
            result["enum"] = self.enum
        
        if self.items:
            result["items"] = self.items
        
        return result


@dataclass
class ToolSchema:
    """工具Schema"""
    name: str
    description: str
    parameters: List[ToolParameter] = None
    returns: Optional[Dict] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: p.to_dict() 
                    for p in self.parameters
                },
                "required": [
                    p.name for p in self.parameters 
                    if p.required
                ]
            },
            "returns": self.returns
        }


# 示例：定义一个数据库查询工具的Schema
def create_database_tool_schema() -> ToolSchema:
    """创建数据库工具Schema"""
    return ToolSchema(
        name="database",
        description="执行SQL查询和数据库操作",
        parameters=[
            ToolParameter(
                name="operation",
                description="操作类型：query（查询）或execute（执行）",
                type=ParameterType.STRING,
                required=True,
                enum=["query", "execute"]
            ),
            ToolParameter(
                name="sql",
                description="SQL语句",
                type=ParameterType.STRING,
                required=True
            ),
            ToolParameter(
                name="params",
                description="SQL参数",
                type=ParameterType.ARRAY,
                required=False,
                default=[]
            )
        ],
        returns={
            "description": "查询返回结果列表，执行返回受影响行数",
            "type": "object"
        }
    )


# 示例：定义一个文件操作工具的Schema
def create_file_tool_schema() -> ToolSchema:
    """创建文件操作工具Schema"""
    return ToolSchema(
        name="file",
        description="读取、写入和操作文件",
        parameters=[
            ToolParameter(
                name="operation",
                description="操作类型：read、write、delete、list",
                type=ParameterType.STRING,
                required=True,
                enum=["read", "write", "delete", "list"]
            ),
            ToolParameter(
                name="path",
                description="文件路径",
                type=ParameterType.STRING,
                required=True
            ),
            ToolParameter(
                name="content",
                description="写入文件的内容（write操作时需要）",
                type=ParameterType.STRING,
                required=False
            )
        ]
    )


# 示例：定义一个HTTP请求工具的Schema
def create_http_tool_schema() -> ToolSchema:
    """创建HTTP请求工具Schema"""
    return ToolSchema(
        name="http",
        description="发送HTTP请求",
        parameters=[
            ToolParameter(
                name="method",
                description="HTTP方法",
                type=ParameterType.STRING,
                required=True,
                enum=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),
            ToolParameter(
                name="url",
                description="请求URL",
                type=ParameterType.STRING,
                required=True
            ),
            ToolParameter(
                name="headers",
                description="请求头",
                type=ParameterType.OBJECT,
                required=False,
                default={}
            ),
            ToolParameter(
                name="body",
                description="请求体",
                type=ParameterType.OBJECT,
                required=False
            )
        ],
        returns={
            "description": "HTTP响应包含status、headers和body",
            "type": "object"
        }
    )


# 打印示例Schema
print("数据库工具Schema:")
print(json.dumps(create_database_tool_schema().to_dict(), indent=2, ensure_ascii=False))
