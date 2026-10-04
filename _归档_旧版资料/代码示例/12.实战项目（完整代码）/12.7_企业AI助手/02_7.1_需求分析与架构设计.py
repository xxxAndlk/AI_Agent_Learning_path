"""
企业AI助手 - 完整架构设计
包含权限管理、审计日志、工具集成等企业级功能
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import uuid
import logging
from abc import ABC, abstractmethod


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"           # 管理员
    HR = "hr"                 # 人事
    FINANCE = "finance"       # 财务
    IT = "it"                 # IT支持
    EMPLOYEE = "employee"    # 普通员工
    GUEST = "guest"          # 访客


class IntentType(str, Enum):
    """意图类型枚举"""
    KNOWLEDGE_QUERY = "knowledge_query"    # 知识查询
    BOOK_MEETING = "book_meeting"          # 预约会议
    SEND_EMAIL = "send_email"              # 发送邮件
    CREATE_TASK = "create_task"            # 创建任务
    HR_POLICY = "hr_policy"                # 人事政策
    IT_SUPPORT = "it_support"             # IT支持
    FINANCE_QUERY = "finance_query"         # 财务查询
    GENERAL = "general"                    # 一般对话


@dataclass
class User:
    """用户模型"""
    user_id: str
    username: str
    email: str
    role: UserRole
    department: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    permissions: List[str] = field(default_factory=list)
    
    def has_permission(self, permission: str) -> bool:
        """检查用户是否有特定权限"""
        if self.role == UserRole.ADMIN:
            return True
        return permission in self.permissions


@dataclass
class ChatMessage:
    """聊天消息"""
    message_id: str
    session_id: str
    user_id: str
    role: str  # user, assistant, system
    content: str
    intent: Optional[IntentType] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "role": self.role,
            "content": self.content,
            "intent": self.intent.value if self.intent else None,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AuditLog:
    """审计日志"""
    log_id: str
    user_id: str
    action: str
    resource: str
    details: Dict
    ip_address: str = ""
    user_agent: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat()
        }
