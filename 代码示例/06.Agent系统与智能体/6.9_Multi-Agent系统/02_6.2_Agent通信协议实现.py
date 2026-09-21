"""
Agent通信协议实现
定义标准化的Agent间通信机制
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import uuid

class MessageType(Enum):
    """消息类型枚举"""
    REQUEST = "request"                 # 请求消息
    RESPONSE = "response"               # 响应消息
    BROADCAST = "broadcast"             # 广播消息
    HEARTBEAT = "heartbeat"             # 心跳消息
    ERROR = "error"                     # 错误消息
    TASK_ASSIGN = "task_assign"         # 任务分配
    TASK_RESULT = "task_result"         # 任务结果
    COORDINATION = "coordination"       # 协调消息


class Priority(Enum):
    """消息优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentMessage:
    """标准Agent消息格式"""
    # 消息标识
    message_id: str  # 消息唯一ID
    correlation_id: Optional[str]  # 关联ID（用于请求-响应匹配）
    
    # 路由信息
    sender_id: str  # 发送者ID
    receiver_id: str  # 接收者ID，"broadcast"表示广播
    
    # 消息内容
    msg_type: MessageType  # 消息类型
    payload: Dict[str, Any]  # 消息负载
    
    # 元数据
    timestamp: datetime  # 时间戳
    priority: Priority = Priority.NORMAL  # 优先级
    ttl: int = 300  # 生存时间（秒）
    
    # 扩展字段
    metadata: Optional[Dict] = None  # 额外元数据
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.msg_type, str):
            self.msg_type = MessageType(self.msg_type)  # 字符串转换为枚举
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)  # 字符串转换为枚举
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "msg_type": self.msg_type.value,  # 枚举转字符串
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),  # 时间转字符串
            "priority": self.priority.value,  # 枚举转整数
            "ttl": self.ttl,
            "metadata": self.metadata or {}  # 空字典默认值
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        """从字典创建消息"""
        return cls(
            message_id=data["message_id"],
            correlation_id=data.get("correlation_id"),
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            msg_type=MessageType(data["msg_type"]),  # 字符串转枚举
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),  # 字符串转时间
            priority=Priority(data.get("priority", 2)),
            ttl=data.get("ttl", 300),
            metadata=data.get("metadata")
        )
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """从JSON字符串创建消息"""
        return cls.from_dict(json.loads(json_str))


class CommunicationProtocol:
    """Agent通信协议"""
    
    @staticmethod
    def create_request(
        sender_id: str,
        receiver_id: str,
        action: str,
        params: Dict = None,
        priority: Priority = Priority.NORMAL
    ) -> AgentMessage:
        """创建请求消息"""
        return AgentMessage(
            message_id=str(uuid.uuid4()),  # 生成唯一ID
            correlation_id=None,  # 请求暂无关联ID
            sender_id=sender_id,  # 设置发送者
            receiver_id=receiver_id,  # 设置接收者
            msg_type=MessageType.REQUEST,  # 设置消息类型
            payload={
                "action": action,  # 要执行的动作
                "params": params or {}  # 参数
            },
            timestamp=datetime.now(),  # 当前时间
            priority=priority  # 优先级
        )
    
    @staticmethod
    def create_response(
        request_msg: AgentMessage,
        result: Any,
        success: bool = True
    ) -> AgentMessage:
        """创建响应消息"""
        return AgentMessage(
            message_id=str(uuid.uuid4()),  # 生成新的唯一ID
            correlation_id=request_msg.message_id,  # 关联请求ID
            sender_id=request_msg.receiver_id,  # 发送者是原请求的接收者
            receiver_id=request_msg.sender_id,  # 接收者是原请求的发送者
            msg_type=MessageType.RESPONSE,  # 设置消息类型
            payload={
                "success": success,  # 执行是否成功
                "result": result,  # 执行结果
                "original_action": request_msg.payload.get("action")  # 原动作
            },
            timestamp=datetime.now(),  # 当前时间
            priority=request_msg.priority  # 继承请求的优先级
        )
    
    @staticmethod
    def create_task_assign(
        sender_id: str,
        receiver_id: str,
        task_id: str,
        task_type: str,
        description: str,
        deadline: Optional[datetime] = None
    ) -> AgentMessage:
        """创建任务分配消息"""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            msg_type=MessageType.TASK_ASSIGN,
            payload={
                "task_id": task_id,  # 任务ID
                "task_type": task_type,  # 任务类型
                "description": description,  # 任务描述
                "deadline": deadline.isoformat() if deadline else None  # 截止时间
            },
            timestamp=datetime.now(),
            priority=Priority.HIGH  # 任务分配高优先级
        )
    
    @staticmethod
    def create_heartbeat(sender_id: str, status: str = "active") -> AgentMessage:
        """创建心跳消息"""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id="broadcast",  # 广播心跳
            msg_type=MessageType.HEARTBEAT,
            payload={
                "status": status,  # Agent状态
                "timestamp": datetime.now().isoformat()  # 时间戳
            },
            timestamp=datetime.now(),
            priority=Priority.LOW,  # 心跳低优先级
            ttl=60  # 短TTL
        )


class MessageBroker:
    """消息代理
    
    负责消息的路由、转发和队列管理
    """
    
    def __init__(self):
        """初始化消息代理"""
        self.queues: Dict[str, List[AgentMessage]] = {}  # Agent消息队列
        self.subscribers: Dict[str, List[str]] = {}  # 广播订阅者
        self.message_history: List[AgentMessage] = []  # 消息历史
        self.max_history = 1000  # 最大历史记录数
    
    def register_agent(self, agent_id: str):
        """注册Agent"""
        if agent_id not in self.queues:
            self.queues[agent_id] = []  # 初始化消息队列
            self.subscribers[agent_id] = []  # 初始化订阅列表
    
    def send_message(self, message: AgentMessage) -> bool:
        """发送消息"""
        # 检查消息是否过期
        age = (datetime.now() - message.timestamp).total_seconds()
        if age > message.ttl:
            return False  # 过期消息丢弃
        
        # 添加到历史记录
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)  # 超过限制时删除最早的
        
        # 路由消息
        if message.receiver_id == "broadcast":
            # 广播消息：发送给所有其他Agent
            for agent_id in self.queues:
                if agent_id != message.sender_id:
                    self.queues[agent_id].append(message)
        else:
            # 点对点消息：只发送给目标
            if message.receiver_id in self.queues:
                self.queues[message.receiver_id].append(message)
            else:
                return False  # 目标不存在
        
        return True  # 发送成功
    
    def get_messages(self, agent_id: str, limit: int = 10) -> List[AgentMessage]:
        """获取Agent的消息"""
        if agent_id not in self.queues:
            return []  # Agent不存在返回空
        
        # 获取消息并从队列中移除
        messages = self.queues[agent_id][:limit]
        self.queues[agent_id] = self.queues[agent_id][limit:]
        return messages
    
    def subscribe_broadcast(self, agent_id: str, topic: str = "default"):
        """订阅广播"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []  # 初始化主题订阅
        if agent_id not in self.subscribers[topic]:
            self.subscribers[topic].append(agent_id)  # 添加订阅


# 使用示例
if __name__ == "__main__":
    # 创建消息
    request = CommunicationProtocol.create_request(
        sender_id="agent_1",
        receiver_id="agent_2",
        action="compute",
        params={"expression": "15 + 25"}
    )
    
    print("=== 请求消息 ===")
    print(request.to_json())
    
    # 创建响应
    response = CommunicationProtocol.create_response(
        request_msg=request,
        result=40,
        success=True
    )
    
    print("\n=== 响应消息 ===")
    print(response.to_json())
    
    # 创建任务分配
    task_msg = CommunicationProtocol.create_task_assign(
        sender_id="manager",
        receiver_id="worker_1",
        task_id="task_001",
        task_type="analysis",
        description="分析Q3销售数据"
    )
    
    print("\n=== 任务分配消息 ===")
    print(task_msg.to_json())
