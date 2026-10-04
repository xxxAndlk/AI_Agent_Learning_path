"""
工单状态处理器
使用EnumOutputParser实现工单状态流转
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import EnumOutputParser
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

# ============================================================
# 定义工单状态枚举
# ============================================================
class TicketStatus(Enum):
    """工单状态"""
    NEW = "新建"
    ASSIGNED = "已分配"
    IN_PROGRESS = "处理中"
    WAITING = "等待中"
    RESOLVED = "已解决"
    CLOSED = "已关闭"
    REOPENED = "已重开"

# ============================================================
# 定义工单模型
# ============================================================
class Ticket(BaseModel):
    """工单模型"""
    id: str = Field(description="工单ID")
    title: str = Field(description="工单标题")
    status: TicketStatus = Field(description="当前状态")
    assignee: Optional[str] = Field(default=None, description="处理人")
    priority: str = Field(description="优先级")

# ============================================================
# 状态解析器
# ============================================================
status_parser = EnumOutputParser(enum=TicketStatus)

prompt = ChatPromptTemplate.from_template(
    "根据工单描述判断当前状态。\n\n"
    "工单内容：{description}\n\n"
    "当前状态：{current_status}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | status_parser

# ============================================================
# 模拟工单状态流转
# ============================================================
class TicketStateMachine:
    """工单状态机"""
    
    # 定义状态流转规则
    TRANSITIONS = {
        TicketStatus.NEW: [TicketStatus.ASSIGNED],
        TicketStatus.ASSIGNED: [TicketStatus.IN_PROGRESS, TicketStatus.CLOSED],
        TicketStatus.IN_PROGRESS: [TicketStatus.WAITING, TicketStatus.RESOLVED],
        TicketStatus.WAITING: [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED],
        TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.REOPENED],
        TicketStatus.CLOSED: [TicketStatus.REOPENED],
        TicketStatus.REOPENED: [TicketStatus.IN_PROGRESS, TicketStatus.CLOSED]
    }
    
    @classmethod
    def can_transition(cls, from_status: TicketStatus, to_status: TicketStatus) -> bool:
        """检查状态转换是否合法"""
        allowed = cls.TRANSITIONS.get(from_status, [])
        return to_status in allowed
    
    @classmethod
    def process_status_change(cls, description: str, current_status: TicketStatus):
        """处理状态变更"""
        new_status = chain.invoke({
            "description": description,
            "current_status": current_status.value
        })
        
        # 验证状态转换是否合法
        if cls.can_transition(current_status, new_status):
            return new_status
        else:
            raise ValueError(
                f"非法状态转换: {current_status.value} -> {new_status.value}"
            )

# 测试状态机
print("测试工单状态流转：")
current = TicketStatus.NEW

# 模拟处理流程
test_scenario = "工程师已经收到工单并开始查看问题"

try:
    new_status = TicketStateMachine.process_status_change(
        test_scenario, 
        current
    )
    print(f"状态转换: {current.value} -> {new_status.value}")
    print("转换合法！")
except ValueError as e:
    print(f"错误: {e}")
