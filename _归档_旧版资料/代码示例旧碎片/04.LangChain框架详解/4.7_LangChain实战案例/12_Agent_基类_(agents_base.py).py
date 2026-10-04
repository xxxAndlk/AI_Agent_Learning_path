"""
Agent 基类
定义所有 Agent 的通用接口和行为
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Agent 配置"""
    name: str
    description: str
    system_prompt: str
    model_name: str = "gpt-5.4-mini"
    temperature: float = 0.7
    max_iterations: int = 5
    verbose: bool = False


class Message(BaseModel):
    """Agent 消息"""
    sender: str
    receiver: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: Optional[BaseChatModel] = None,
    ):
        """
        初始化 Agent
        
        Args:
            config: Agent 配置
            llm: 语言模型实例
        """
        self.config = config
        self.llm = llm
        self.message_history: List[Message] = []
        self.context: Dict[str, Any] = {}
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        处理输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        pass
    
    def set_llm(self, llm: BaseChatModel):
        """设置语言模型"""
        self.llm = llm
    
    def add_message(self, message: Message):
        """添加消息到历史"""
        self.message_history.append(message)
    
    def get_messages(
        self,
        sender: Optional[str] = None,
        receiver: Optional[str] = None,
    ) -> List[Message]:
        """获取消息历史"""
        messages = self.message_history
        
        if sender:
            messages = [m for m in messages if m.sender == sender]
        if receiver:
            messages = [m for m in messages if m.receiver == receiver]
        
        return messages
    
    def clear_history(self):
        """清空消息历史"""
        self.message_history.clear()
    
    def update_context(self, key: str, value: Any):
        """更新上下文"""
        self.context[key] = value
    
    def get_context(self, key: str) -> Any:
        """获取上下文"""
        return self.context.get(key)
    
    def call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
    ) -> str:
        """调用语言模型"""
        if self.llm is None:
            raise ValueError("LLM 未设置")
        
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))
        
        response = self.llm.invoke(messages)
        return response.content
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.config.name})>"
