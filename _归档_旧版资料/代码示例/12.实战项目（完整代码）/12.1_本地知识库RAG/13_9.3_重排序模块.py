# src/retrieval/reranker.py
# 重排序模块
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import logging
import numpy as np

logger = logging.getLogger(__name__)


class Reranker:
    """重排序器
    
    在初步检索之后，对结果进行重新排序
    使用更精确（但更慢）的模型来评估文档与查询的相关性
    
    常用模型：
    - BAAI/bge-reranker-base
    - BAAI/bge-reranker-large
    - cross-encoder/ms-marco-MiniLM-L-6-v2
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """
        参数:
            model_name: 重排序模型名称
        """
        self.model_name = model_name
        
        logger.info(f"加载重排序模型: {model_name}")
        self.cross_encoder = HuggingFaceCrossEncoder(
            model_name=model_name,
            max_length=512
        )
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: Optional[int] = None
    ) -> List[Document]:
        """重排序文档
        
        参数:
            query: 用户查询
            documents: 待重排序的文档列表
            top_n: 返回前N个结果，None表示返回全部
        返回:
            重排序后的文档列表
        """
        if not documents:
            return []
        
        # 准备文档对
        doc_scores = []
        
        for doc in documents:
            # 构建查询-文档对
            pairs = [query, doc.page_content]
            score = self.cross_encoder.score(pairs)
            doc_scores.append((doc, score))
        
        # 按分数降序排序
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 截取前N个
        if top_n is not None:
            doc_scores = doc_scores[:top_n]
        
        # 返回排序后的文档
        reranked_docs = []
        for doc, score in doc_scores:
            # 添加重排序分数到元数据
            doc.metadata["rerank_score"] = score
            reranked_docs.append(doc)
        
        logger.info(f"重排序完成，返回 {len(reranked_docs)} 个文档")
        
        return reranked_docs
    
    def rerank_with_scores(
        self,
        query: str,
        documents: List[Document],
        top_n: Optional[int] = None
    ) -> List[tuple]:
        """重排序并返回分数
        
        参数:
            query: 用户查询
            documents: 待重排序的文档列表
            top_n: 返回前N个结果
        返回:
            (文档, 分数)元组列表
        """
        if not documents:
            return []
        
        # 批量计算分数
        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.cross_encoder.score(pairs)
        
        # 组合文档和分数
        doc_scores = list(zip(documents, scores))
        
        # 排序
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 截取
        if top_n is not None:
            doc_scores = doc_scores[:top_n]
        
        return doc_scores


class CrossEncoderReranker(Reranker):
    """CrossEncoder重排序器
    
    使用CrossEncoder进行更精确的相关性评估
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        super().__init__(model_name)


class BGEReranker(Reranker):
    """BGE重排序器
    
    使用BGE系列的reranker模型
    专门针对中文优化
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        super().__init__(model_name)


class LearningToRankReranker(Reranker):
    """学习排序重排序器
    
    使用传统LTR方法
    基于文档的多个特征进行排序
    """
    
    def __init__(self):
        super().__init__(model_name=None)
        self.cross_encoder = None  # 不使用神经网络模型
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: Optional[int] = None
    ) -> List[Document]:
        """基于特征的LTR重排序
        
        使用以下特征：
        - BM25分数
        - 文本长度
        - 关键词匹配
        - 查询词密度
        """
        if not documents:
            return []
        
        doc_scores = []
        
        for doc in documents:
            score = self._compute_features(query, doc)
            doc_scores.append((doc, score))
        
        # 排序
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        if top_n:
            doc_scores = doc_scores[:top_n]
        
        # 返回
        return [doc for doc, _ in doc_scores]
    
    def _compute_features(self, query: str, doc: Document) -> float:
        """计算文档特征分数
        
        参数:
            query: 查询
            doc: 文档
        返回:
            综合分数
        """
        score = 0.0
        
        # 1. 关键词匹配
        query_terms = set(query.lower().split())
        doc_terms = set(doc.page_content.lower().split())
        overlap = query_terms & doc_terms
        score += len(overlap) / len(query_terms) if query_terms else 0
        
        # 2. 查询词密度（查询词在文档中出现的频率）
        density = sum(doc.page_content.lower().count(term) for term in query_terms)
        score += density / 1000  # 归一化
        
        # 3. 位置分数（查询词越靠前分数越高）
        for term in query_terms:
            pos = doc.page_content.lower().find(term)
            if pos >= 0:
                score += 1.0 / (pos + 1)
        
        # 4. 标题匹配（如果在元数据中有标题）
        if "heading" in doc.metadata and doc.metadata["heading"]:
            heading = doc.metadata["heading"].lower()
            if any(term in heading for term in query_terms):
                score += 2.0
        
        return score


class HybridReranker:
    """混合重排序器
    
    结合多种重排序方法
    """
    
    def __init__(
        self,
        primary_reranker: Reranker = None,
        fallback_reranker: Reranker = None
    ):
        """
        参数:
            primary_reranker: 主要重排序器
            fallback_reranker: 备用重排序器
        """
        self.primary_reranker = primary_reranker
        self.fallback_reranker = fallback_reranker
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: Optional[int] = None
    ) -> List[Document]:
        """混合重排序
        
        尝试使用主重排序器，失败则使用备用
        """
        try:
            if self.primary_reranker:
                return self.primary_reranker.rerank(query, documents, top_n)
        except Exception as e:
            logger.warning(f"主重排序器失败: {e}")
        
        try:
            if self.fallback_reranker:
                return self.fallback_reranker.rerank(query, documents, top_n)
        except Exception as e:
            logger.warning(f"备用重排序器失败: {e}")
        
        # 回退到不重排序
        return documents[:top_n] if top_n else documents


# 使用示例
if __name__ == "__main__":
    # 创建示例文档
    from langchain_core.documents import Document
    
    docs = [
        Document(
            page_content="人工智能是计算机科学的一个分支，致力于创建智能机器。",
            metadata={"source": "doc1"}
        ),
        Document(
            page_content="机器学习是人工智能的一个重要子领域。",
            metadata={"source": "doc2"}
        ),
        Document(
            page_content="深度学习使用多层神经网络来学习数据的表示。",
            metadata={"source": "doc3"}
        ),
    ]
    
    # 使用重排序器
    reranker = BGEReranker(model_name="BAAI/bge-reranker-base")
    
    # 重排序
    reranked = reranker.rerank("什么是人工智能？", docs, top_n=2)
    
    print("重排序结果:")
    for i, doc in enumerate(reranked):
        score = doc.metadata.get("rerank_score", 0)
        print(f"{i+1}. 分数: {score:.4f}")
        print(f"   内容: {doc.page_content[:50]}...")
