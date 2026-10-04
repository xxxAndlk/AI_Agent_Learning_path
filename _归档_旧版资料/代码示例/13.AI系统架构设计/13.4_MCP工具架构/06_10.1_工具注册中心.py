"""
MCP工具注册中心
支持动态注册、发现和管理工具
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib


@dataclass
class ToolMetadata:
    """工具元数据"""
    name: str
    description: str
    version: str
    author: str
    registered_at: datetime
    last_used: Optional[datetime] = None
    usage_count: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self.tools: Dict[str, MCPToolBase] = {}
        self.metadata: Dict[str, ToolMetadata] = {}
        self.hooks: Dict[str, List[Callable]] = {
            "before_call": [],
            "after_call": [],
            "on_error": []
        }
    
    def register(
        self,
        tool: MCPToolBase,
        version: str = "1.0.0",
        author: str = "unknown",
        tags: List[str] = None
    ) -> bool:
        """注册工具"""
        if tool.name in self.tools:
            return False
        
        self.tools[tool.name] = tool
        self.metadata[tool.name] = ToolMetadata(
            name=tool.name,
            description=tool.description,
            version=version,
            author=author,
            registered_at=datetime.now(),
            tags=tags or []
        )
        
        # 触发注册钩子
        self._trigger_hook("after_register", tool)
        
        return True
    
    def unregister(self, tool_name: str) -> bool:
        """注销工具"""
        if tool_name not in self.tools:
            return False
        
        del self.tools[tool_name]
        del self.metadata[tool_name]
        
        return True
    
    def get_tool(self, tool_name: str) -> Optional[MCPToolBase]:
        """获取工具"""
        tool = self.tools.get(tool_name)
        
        if tool and tool_name in self.metadata:
            # 更新使用统计
            meta = self.metadata[tool_name]
            meta.usage_count += 1
            meta.last_used = datetime.now()
        
        return tool
    
    def list_tools(
        self,
        tag: str = None,
        search: str = None
    ) -> List[Dict]:
        """列出工具"""
        tools = []
        
        for name, tool in self.tools.items():
            meta = self.metadata.get(name)
            
            # 标签过滤
            if tag and tag not in (meta.tags or []):
                continue
            
            # 搜索过滤
            if search:
                if (search.lower() not in name.lower() and 
                    search.lower() not in tool.description.lower()):
                    continue
            
            tools.append({
                "name": name,
                "description": tool.description,
                "version": meta.version,
                "author": meta.author,
                "usage_count": meta.usage_count,
                "tags": meta.tags
            })
        
        return tools
    
    def add_hook(self, event: str, callback: Callable):
        """添加钩子"""
        if event in self.hooks:
            self.hooks[event].append(callback)
    
    def _trigger_hook(self, event: str, *args, **kwargs):
        """触发钩子"""
        for callback in self.hooks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"钩子执行错误: {e}")


# 工具权限管理
class ToolPermission:
    """工具权限管理"""
    
    def __init__(self):
        self.permissions: Dict[str, List[str]] = {}  # tool_name -> [allowed_roles]
        self.denials: Dict[str, List[str]] = {}  # tool_name -> [denied_roles]
    
    def allow(self, tool_name: str, roles: List[str]):
        """设置允许的角色"""
        self.permissions[tool_name] = roles
    
    def deny(self, tool_name: str, roles: List[str]):
        """设置拒绝的角色"""
        self.denials[tool_name] = roles
    
    def check_permission(self, tool_name: str, user_role: str) -> bool:
        """检查权限"""
        # 检查拒绝列表
        if tool_name in self.denials:
            if user_role in self.denials[tool_name]:
                return False
        
        # 检查允许列表
        if tool_name in self.permissions:
            return user_role in self.permissions[tool_name]
        
        # 默认允许
        return True
