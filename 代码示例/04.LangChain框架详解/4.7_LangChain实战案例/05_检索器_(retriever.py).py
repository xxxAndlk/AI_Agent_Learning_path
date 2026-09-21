"""
检索器模块
提供高级检索功能
"""
import logging
from typing import List, Optional, Tuple
from langchain_core.documents import Document
from langchain_community.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class AdvancedRetriever:
    """高级检索器"""
    
    def __init__(
        self,
        base_retriever,
        llm: Optional[ChatOpenAI] = None,
        use_compression: bool = False,
    ):
        """
        初始化高级检索器
        
        Args:
            base_retriever: 基础检索器
            llm: LLM 模型（用于压缩）
            use_compression: 是否使用文档压缩
        """
        self.base_retriever = base_retriever
        self.llm = llm
        self.use_compression = use_compression
        
        if use_compression and llm is None:
            raise ValueError("使用文档压缩时需要提供 LLM")
    
    def get_compression_retriever(self) -> ContextualCompressionRetriever:
        """获取带压缩的检索器"""
        if not self.use_compression or self.llm is None:
            return self.base_retriever
        
        compressor = LLMChainExtractor.from_llm(self.llm)
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.base_retriever,
        )
    
    def search(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> List[Document]:
        """
        检索文档
        
        Args:
            query: 查询字符串
            k: 返回数量（覆盖默认配置）
            
        Returns:
            检索到的文档列表
        """
        if k:
            self.base_retriever.search_kwargs["k"] = k
        
        docs = self.base_retriever.invoke(query)
        logger.info(f"检索到 {len(docs)} 个相关文档")
        return docs
    
    def search_with_score(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Tuple[Document, float]]:
        """
        检索文档并返回相似度分数
        
        Args:
            query: 查询字符串
            k: 返回数量
            score_threshold: 相似度阈值
            
        Returns:
            (文档, 分数) 元组列表
        """
        docs_with_scores = self.base_retriever.similarity_search_with_score(
            query,
            k=k,
        )
        
        # 可选：按阈值过滤
        if score_threshold:
            docs_with_scores = [
                (doc, score) for doc, score in docs_with_scores
                if score >= score_threshold
            ]
        
        logger.info(
            f"检索到 {len(docs_with_scores)} 个文档 "
            f"(阈值: {score_threshold})"
        )
        return docs_with_scores
    
    def get_relevant_documents(
        self,
        query: str,
    ) -> List[Document]:
        """获取相关文档（兼容 LangChain 接口）"""
        return self.search(query)
    
    async def aget_relevant_documents(
        self,
        query: str,
    ) -> List[Document]:
        """异步获取相关文档"""
        return self.search(query)
