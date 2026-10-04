# 需要先安装: pip install langchain langchain-community langchain-openai

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from typing import List

class RAGVectorStore:
    """基于FAISS的RAG向量存储"""
    
    def __init__(self, api_key: str, embedding_model: str = "text-embedding-3-small"):
        self.embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model=embedding_model
        )
        self.vectorstore = None
        
    def create_from_texts(self, texts: List[str], metadatas: List[dict] = None):
        """
        从文本创建向量存储
        
        参数:
            texts: 文本列表
            metadatas: 元数据列表
        """
        self.vectorstore = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
    def similarity_search(self, query: str, k: int = 4) -> List[dict]:
        """相似度搜索"""
        docs = self.vectorstore.similarity_search(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    
    def as_retriever(self, search_type: str = "similarity", k: int = 4):
        """转换为LangChain Retriever"""
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )


# 使用示例
if __name__ == "__main__":
    # 注意：需要设置OPENAI_API_KEY环境变量
    import os
    api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")
    
    # 文档内容
    documents = [
        "Python是一种高级编程语言，简洁易读。",
        "Java是一种面向对象编程语言，跨平台运行。",
        "机器学习是人工智能的一个分支，研究如何让计算机学习。",
        "深度学习是机器学习的子领域，使用神经网络模型。",
        "向量数据库专门用于存储和检索向量数据。",
    ]
    
    # 元数据
    metadatas = [
        {"source": "python-docs"},
        {"source": "java-docs"},
        {"source": "ml-book"},
        {"source": "dl-book"},
        {"source": "vector-db"},
    ]
    
    # 创建向量存储
    store = RAGVectorStore(api_key)
    store.create_from_texts(documents, metadatas)
    
    # 搜索
    query = "什么是深度学习？"
    results = store.similarity_search(query, k=3)
    
    print(f"查询: {query}")
    print("\n搜索结果:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['content']}")
        print(f"   来源: {result['metadata']['source']}")
