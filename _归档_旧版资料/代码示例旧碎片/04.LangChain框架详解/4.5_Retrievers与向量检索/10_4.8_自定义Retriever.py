# custom_retriever.py
# 自定义检索器示例

from typing import List
from langchain_core.documents import Document, BaseRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import numpy as np


class CustomKeywordRetriever(BaseRetriever):
    """
    自定义关键词检索器
    
    这是一个简单的关键词匹配检索器
    实际应用中可以根据业务需求实现更复杂的逻辑
    """
    
    def __init__(self, documents: List[Document], top_k: int = 3):
        self.documents = documents
        self.top_k = top_k
        # 构建关键词索引
        self.keyword_index = self._build_keyword_index()
    
    def _build_keyword_index(self):
        """构建简单的关键词到文档的映射"""
        keyword_index = {}
        for i, doc in enumerate(self.documents):
            # 提取关键词（简单按空格分词）
            words = doc.page_content.lower().split()
            for word in words:
                if word not in keyword_index:
                    keyword_index[word] = []
                keyword_index[word].append(i)
        return keyword_index
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """检索与查询关键词匹配的文档"""
        query_words = query.lower().split()
        
        # 统计每个文档的匹配次数
        doc_scores = {}
        for word in query_words:
            if word in self.keyword_index:
                for doc_idx in self.keyword_index[word]:
                    doc_scores[doc_idx] = doc_scores.get(doc_idx, 0) + 1
        
        # 按分数排序
        sorted_indices = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 返回top_k个文档
        results = []
        for idx, score in sorted_indices[:self.top_k]:
            doc = self.documents[idx]
            results.append(doc)
        
        return results


class HybridRetriever(BaseRetriever):
    """
    自定义混合检索器
    
    结合关键词检索和向量检索的结果
    """
    
    def __init__(
        self,
        documents: List[Document],
        embeddings: OpenAIEmbeddings,
        top_k: int = 3
    ):
        self.documents = documents
        self.embeddings = embeddings
        self.top_k = top_k
        
        # 创建向量数据库
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name="hybrid"
        )
        
        # 关键词检索器
        self.keyword_retriever = CustomKeywordRetriever(documents, top_k * 2)
        
        # 向量检索器
        self.vector_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": top_k * 2}
        )
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """执行混合检索"""
        
        # 关键词检索结果
        keyword_results = self.keyword_retriever.invoke(query)
        
        # 向量检索结果
        vector_results = self.vector_retriever.invoke(query)
        
        # 合并结果，使用RRF算法
        combined = self._reciprocal_rank_fusion(keyword_results, vector_results)
        
        return combined[:self.top_k]
    
    def _reciprocal_rank_fusion(self, list1: List[Document], list2: List[Document], k: int = 60):
        """RRF融合算法"""
        doc_scores = {}
        
        # 处理第一个列表
        for rank, doc in enumerate(list1):
            key = doc.page_content
            doc_scores[key] = doc_scores.get(key, 0) + 1 / (k + rank + 1)
        
        # 处理第二个列表
        for rank, doc in enumerate(list2):
            key = doc.page_content
            doc_scores[key] = doc_scores.get(key, 0) + 1 / (k + rank + 1)
        
        # 排序
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 获取原始文档对象
        doc_map = {doc.page_content: doc for doc in list1 + list2}
        
        return [doc_map[key] for key, _ in sorted_docs]


class AdaptiveRetriever(BaseRetriever):
    """
    自适应检索器
    
    根据查询类型自动选择合适的检索策略
    """
    
    def __init__(self, vectorstore, llm=None):
        self.vectorstore = vectorstore
        self.llm = llm
        self.vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    def _classify_query(self, query: str) -> str:
        """
        简单查询分类
        实际可以使用LLM或更复杂的分类器
        """
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["什么", "什么是", "解释", "定义", "what", "what is"]):
            return "definition"
        elif any(kw in query_lower for kw in ["如何", "怎样", "怎么", "how to", "how do"]):
            return "howto"
        elif any(kw in query_lower for kw in ["列表", "有哪些", "哪些", "list", "what are"]):
            return "list"
        else:
            return "general"
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """根据查询类型选择检索策略"""
        
        query_type = self._classify_query(query)
        
        # 针对不同查询类型使用不同的检索参数
        if query_type == "definition":
            # 定义类查询：优先返回简短精确的内容
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 2}
            )
        elif query_type == "howto":
            # 操作类查询：返回详细步骤
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            )
        elif query_type == "list":
            # 列表类查询：返回多个相关项
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            )
        else:
            retriever = self.vector_retriever
        
        return retriever.invoke(query)


def use_custom_retriever():
    """使用自定义检索器"""
    from langchain_core.documents import Document
    
    # 准备文档
    documents = [
        Document(
            page_content="Python字典是一种键值对数据结构。",
            metadata={"source": "doc1"}
        ),
        Document(
            page_content="Python列表是有序的元素集合。",
            metadata={"source": "doc2"}
        ),
        Document(
            page_content="Python集合是无序且不重复的元素集合。",
            metadata={"source": "doc3"}
        ),
    ]
    
    # 使用关键词检索器
    keyword_retriever = CustomKeywordRetriever(documents, top_k=2)
    results = keyword_retriever.invoke("Python 数据结构")
    print("【关键词检索】")
    for doc in results:
        print(f"  - {doc.page_content}")
    
    # 使用混合检索器
    embeddings = OpenAIEmbeddings()
    hybrid_retriever = HybridRetriever(documents, embeddings, top_k=2)
    results = hybrid_retriever.invoke("Python 字典")
    print("\n【混合检索】")
    for doc in results:
        print(f"  - {doc.page_content}")


# 运行测试
if __name__ == "__main__":
    use_custom_retriever()
