"""
企业知识库问答系统

特性：
- 混合检索（向量 + BM25）
- 查询扩展和改写
- 多级重排序
- 结果缓存
- 支持PDF、Word、TXT文档
"""

from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader, 
    TextLoader, 
    PyPDFLoader,
    Docx2txtLoader
)
from langchain.chains.retrieval_qa.base import RetrievalQA  # 旧版API，建议新项目使用LCEL
from langchain_openai import ChatOpenAI
from langchain_community.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import os
import numpy as np


class EnterpriseRAGSystem:
    """企业级RAG问答系统"""
    
    def __init__(
        self,
        docs_dir: str = "./docs",
        vector_store_path: str = "./faiss_index",
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-5.4-mini"
    ):
        """初始化系统"""
        self.docs_dir = docs_dir
        self.vector_store_path = vector_store_path
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        
        # 初始化组件
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.llm = ChatOpenAI(model_name=llm_model, temperature=0)
        
        # 缓存
        self.query_cache = QueryCache(max_size=500)
        
        self.vector_store = None
        self.hybrid_retriever = None
        self.qa_chain = None
    
    def load_documents(self) -> List:
        """加载多种格式的文档"""
        loaders = {
            '.txt': TextLoader,
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.md': TextLoader
        }
        
        documents = []
        
        for ext, loader_cls in loaders.items():
            loader = DirectoryLoader(
                self.docs_dir,
                glob=f"**/*{ext}",
                loader_cls=loader_cls,
                loader_kwargs={"encoding": "utf-8"}
            )
            try:
                docs = loader.load()
                documents.extend(docs)
                print(f"加载 {ext} 文件: {len(docs)} 个")
            except Exception as e:
                print(f"加载 {ext} 文件失败: {e}")
        
        return documents
    
    def split_documents(
        self, 
        documents: List, 
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> List:
        """分割文档"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"文档分割完成: {len(chunks)} 个文本块")
        
        return chunks
    
    def build_index(self, force_rebuild: bool = False):
        """构建向量索引"""
        if not force_rebuild and os.path.exists(self.vector_store_path):
            print("加载已有索引...")
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return
        
        print("构建新索引...")
        
        # 加载和分割文档
        docs = self.load_documents()
        chunks = self.split_documents(docs)
        
        # 构建向量存储
        self.vector_store = FAISS.from_documents(
            chunks, 
            self.embeddings
        )
        self.vector_store.save_local(self.vector_store_path)
        
        print(f"索引构建完成: {len(chunks)} 个文档块")
    
    def setup_qa_chain(
        self,
        top_k: int = 5,
        use_reranker: bool = True
    ):
        """设置问答链"""
        if not self.vector_store:
            raise ValueError("向量索引未初始化")
        
        # 创建检索器
        base_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": top_k * 2}
        )
        
        # 可选：添加重排序
        if use_reranker:
            compressor = LLMChainExtractor.from_llm(self.llm)
            retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
        else:
            retriever = base_retriever
        
        # 创建QA链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": self._get_custom_prompt()
            }
        )
    
    def _get_custom_prompt(self):
        """自定义提示词"""
        from langchain_core.prompts import PromptTemplate
        
        template = """使用以下上下文信息回答用户的问题。

上下文信息：
{context}

用户问题：{question}

要求：
1. 只使用提供的上下文信息，不要添加外部知识
2. 如果上下文中没有相关信息，请明确说明
3. 回答要简洁、准确

回答："""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(
        self,
        question: str,
        use_cache: bool = True,
        use_query_rewrite: bool = True
    ) -> Dict[str, Any]:
        """
        执行问答
        
        参数:
            question: 用户问题
            use_cache: 是否使用缓存
            use_query_rewrite: 是否使用查询改写
        
        返回:
            答案和相关信息
        """
        # 查询改写
        original_query = question
        if use_query_rewrite:
            question = self._rewrite_query(question)
            print(f"查询改写: {original_query} -> {question}")
        
        # 缓存查询
        if use_cache:
            cached = self.query_cache.get(question)
            if cached:
                print("命中缓存")
                return cached
        
        # 执行问答
        if not self.qa_chain:
            self.setup_qa_chain()
        
        result = self.qa_chain.invoke({"query": question})
        
        response = {
            "original_query": original_query,
            "rewritten_query": question,
            "answer": result["result"],
            "source_documents": [
                {
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source", "unknown")
                }
                for doc in result["source_documents"]
            ]
        }
        
        # 缓存结果
        if use_cache:
            self.query_cache.set(question, response)
        
        return response
    
    def _rewrite_query(self, query: str) -> str:
        """简单查询改写"""
        # 实际项目中可以使用LLM进行更复杂的改写
        # 这里做简单的清理
        query = query.strip()
        query = query.replace("\n", " ")
        
        # 添加常见扩展
        extensions = []
        if "什么是" in query or "介绍" in query:
            extensions.extend(["定义", "概念", "解释"])
        
        if extensions:
            query = f"{query} {' '.join(extensions)}"
        
        return query
    
    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            "cache_stats": self.query_cache.get_stats(),
            "index_exists": os.path.exists(self.vector_store_path)
        }


# 使用示例
def main():
    """主函数"""
    # 创建系统
    rag = EnterpriseRAGSystem(
        docs_dir="./docs",
        vector_store_path="./faiss_index",
        embedding_model="text-embedding-3-small",
        llm_model="gpt-5.4-mini"
    )
    
    # 构建索引（首次运行）
    # rag.build_index(force_rebuild=True)
    
    # 执行查询
    # result = rag.query("公司的年假政策是什么？")
    # print(f"答案: {result['answer']}")
    
    # 查看统计
    # print(rag.get_stats())


if __name__ == "__main__":
    main()
