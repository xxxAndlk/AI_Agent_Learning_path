from abc import ABC, abstractmethod
from typing import List, Any
from langchain_core.documents import Document, BaseRetriever

class BaseRetriever(ABC):
    """检索器抽象基类"""
    
    @abstractmethod
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """获取相关文档的核心方法"""
        pass
    
    def invoke(self, input: str, config: dict = None) -> List[Document]:
        """
        同步调用接口
        
        参数:
            input: 用户查询字符串
            config: 可选的配置参数（如run_name用于追踪）
            
        返回:
            相关文档列表
        """
        return self._get_relevant_documents(input)
    
    async def ainvoke(self, input: str, config: dict = None) -> List[Document]:
        """异步调用接口"""
        return await self._aget_relevant_documents(input)
    
    def get_config(self, config: dict = None) -> dict:
        """获取运行时配置"""
        return config or {}
