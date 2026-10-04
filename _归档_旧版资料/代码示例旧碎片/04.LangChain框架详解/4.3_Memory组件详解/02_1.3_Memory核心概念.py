from langchain_core.memory import BaseMemory
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage

class BaseMemory(ABC):
    """Memory基类，定义所有内存类型的接口"""
    
    @property
    @abstractmethod
    def memory_variables(self) -> List[str]:
        """返回内存中存储的变量名列表"""
        pass
    
    @abstractmethod
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """加载内存变量，供Chain使用"""
        pass
    
    @abstractmethod
    def save_context(self, inputs: Dict[str, Any], output: str | BaseMessage) -> None:
        """保存对话上下文到内存"""
        pass
    
    def clear(self) -> None:
        """清空内存内容"""
        pass
