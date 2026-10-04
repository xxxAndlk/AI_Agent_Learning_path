"""
完整RAG应用示例：基于FAISS的本地知识库问答系统
"""

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain.chains.retrieval_qa.base import RetrievalQA  # 旧版链API（已迁移至langchain-classic），新项目建议用LCEL
import os
from typing import List

class RAGSystem:
    """RAG检索增强生成系统"""
    
    def __init__(self, persist_path: str = None):
        # 设置API密钥
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
        
        # 初始化embedding模型
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model="gpt-5.4-mini",
            temperature=0
        )
        
        self.vectorstore = None
        self.qa_chain = None
        self.persist_path = persist_path
        
        # 如果存在已保存的索引，则加载
        if persist_path and os.path.exists(persist_path):
            self._load_index()
    
    def _load_index(self):
        """加载已保存的索引"""
        self.vectorstore = FAISS.load_local(
            self.persist_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        self._build_qa_chain()
        print(f"已加载索引: {self.vectorstore.index.ntotal} 个文档")
    
    def add_documents(self, documents: List[str], metadata: List[dict] = None):
        """添加文档到知识库"""
        if metadata is None:
            metadata = [{}] * len(documents)
        
        docs = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(documents, metadata)
        ]
        
        if self.vectorstore is None:
            # 创建新索引
            self.vectorstore = FAISS.from_documents(
                docs, 
                self.embeddings
            )
        else:
            # 追加到现有索引
            self.vectorstore.add_documents(docs)
        
        # 保存索引
        if self.persist_path:
            self.vectorstore.save_local(self.persist_path)
        
        self._build_qa_chain()
        print(f"已添加 {len(documents)} 个文档")
    
    def _build_qa_chain(self):
        """构建问答链"""
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
    
    def query(self, question: str) -> dict:
        """问答"""
        if self.qa_chain is None:
            return {"error": "知识库为空，请先添加文档"}
        
        result = self.qa_chain.invoke({"query": question})
        
        return {
            "answer": result["result"],
            "sources": [
                {
                    "content": doc.page_content[:200],
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]
        }


def demo_rag_system():
    """RAG系统演示"""
    
    # 创建RAG系统
    rag = RAGSystem(persist_path="./data/rag_index")
    
    # 添加知识库文档
    knowledge = [
        "FAISS是Facebook开源的向量相似度搜索库，专门用于大规模向量数据的高效检索。",
        "FAISS支持多种索引类型：Flat（暴力搜索，精确但慢）、IVF（倒排文件，快且精度可调）、HNSW（图索引，超快）、PQ（乘积量化，极度压缩）。",
        "HNSW索引通过构建分层导航小世界图实现高效搜索，搜索时间复杂度为O(log n)。",
        "乘积量化(PQ)将高维向量分割为多个子向量分别量化，可以将存储空间压缩到原来的1/4到1/16。",
        "LangChain提供了与FAISS的深度集成，可以方便地构建RAG应用。",
        "IVF索引通过K-means聚类将向量分组，搜索时只需查找最近的几个聚类，可以大幅提升搜索速度。",
        "RAG（检索增强生成）结合了向量检索和LLM生成，可以有效解决LLM的知识截止和幻觉问题。",
    ]
    
    # 添加到知识库
    rag.add_documents(knowledge)
    
    # 问答测试
    questions = [
        "FAISS支持哪些索引类型？",
        "HNSW索引的原理是什么？",
        "乘积量化如何压缩存储？",
    ]
    
    for q in questions:
        print(f"\n问题: {q}")
        result = rag.query(q)
        print(f"回答: {result['answer']}")
        print("来源文档:")
        for src in result['sources']:
            print(f"  - {src['content']}...")

# demo_rag_system()  # 需要API密钥
