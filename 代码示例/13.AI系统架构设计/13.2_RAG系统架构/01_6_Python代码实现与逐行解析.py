"""
RAG系统架构

分层架构：
┌─────────────────────────────────────────────────────────────┐
│  Ingestion -> Indexing -> Retrieval -> Generation          │
└─────────────────────────────────────────────────────────────┘
"""

from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.chains.retrieval_qa.base import RetrievalQA  # 旧版API，建议新项目使用LCEL
from langchain_openai import ChatOpenAI
import os


class RAGSystem:
    """RAG检索增强生成系统"""
    
    def __init__(
        self,
        docs_dir: str = "./docs",
        vector_store_path: str = "./faiss_index",
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-5.4-mini"
    ):
        """
        初始化RAG系统
        
        参数:
            docs_dir: 文档目录路径
            vector_store_path: 向量存储保存路径
            embedding_model: 嵌入模型名称
            llm_model: LLM模型名称
        """
        self.docs_dir = docs_dir
        self.vector_store_path = vector_store_path
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        
        # 初始化嵌入模型
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name=llm_model,
            temperature=0
        )
        
        self.vector_store = None
        self.qa_chain = None
    
    def load_documents(self) -> List:
        """
        加载文档
        
        返回:
            文档列表
        """
        loader = DirectoryLoader(
            self.docs_dir,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        return loader.load()
    
    def split_documents(self, documents: List, chunk_size: int = 500, chunk_overlap: int = 100) -> List:
        """
        分割文档
        
        参数:
            documents: 文档列表
            chunk_size: 文本块大小
            chunk_overlap: 重叠大小
        
        返回:
            分割后的文档块列表
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        return text_splitter.split_documents(documents)
    
    def build_vector_store(self, chunks: List):
        """
        构建向量存储
        
        参数:
            chunks: 文档块列表
        """
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)
        print(f"✅ 向量存储已构建，包含 {len(chunks)} 个文档块")
    
    def load_vector_store(self) -> bool:
        """
        加载已有的向量存储
        
        返回:
            加载是否成功
        """
        if os.path.exists(self.vector_store_path):
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return True
        return False
    
    def setup_qa_chain(self, top_k: int = 3):
        """
        设置问答链
        
        参数:
            top_k: 检索的文档数量
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化")
        
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": top_k}
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        执行问答
        
        参数:
            question: 用户问题
        
        返回:
            包含答案和源文档的字典
        """
        if not self.qa_chain:
            self.setup_qa_chain()
        
        result = self.qa_chain.invoke({"query": question})
        
        return {
            "answer": result["result"],
            "source_documents": [
                doc.page_content for doc in result["source_documents"]
            ]
        }
    
    def initialize(self, force_rebuild: bool = False):
        """
        初始化RAG系统
        
        参数:
            force_rebuild: 是否强制重建向量存储
        """
        if force_rebuild or not self.load_vector_store():
            # 加载并分割文档
            docs = self.load_documents()
            chunks = self.split_documents(docs)
            
            # 构建向量存储
            self.build_vector_store(chunks)
        
        # 设置问答链
        self.setup_qa_chain()
        print("✅ RAG系统初始化完成")


def main():
    """主函数"""
    # 创建RAG系统
    rag = RAGSystem(
        docs_dir="./docs",
        vector_store_path="./faiss_index"
    )
    
    # 初始化（如果需要构建索引）
    # rag.initialize(force_rebuild=True)
    
    # 执行查询
    # result = rag.query("什么是机器学习？")
    # print(f"答案: {result['answer']}")


if __name__ == "__main__":
    main()
