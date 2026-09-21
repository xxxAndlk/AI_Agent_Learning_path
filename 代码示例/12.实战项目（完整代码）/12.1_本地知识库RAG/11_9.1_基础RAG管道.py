# src/pipeline/rag_pipeline.py
# 完整RAG Pipeline
from typing import List, Optional, Dict, Any, Union
from langchain_core.documents import Document
from langchain.chains import RetrievalQA  # 旧版链式API，仅作演示；新项目建议用LCEL（prompt | llm | parser）组合
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import StrOutputParser
from langchain_community.callbacks import StreamingStdOutCallbackHandler
import logging
from pathlib import Path
import json

from src.loaders.directory_loader import UnifiedDocumentLoader
from src.chunking.recursive_splitter import RecursiveTextSplitter
from src.vectorstores.faiss_store import FAISSVectorStore
from src.vectorstores.chroma_store import ChromaVectorStore
from config.config import Config

logger = logging.getLogger(__name__)


class RAGPipeline:
    """完整的RAG管道
    
    整合文档加载、分块、向量化、检索、问答全流程
    支持多种配置选项
    """
    
    def __init__(
        self,
        vector_store_type: str = "faiss",
        llm_provider: str = "openai",
        embedding_model: str = "openai",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        top_k: int = 3,
        verbose: bool = False
    ):
        """
        参数:
            vector_store_type: 向量存储类型，可选 "faiss", "chroma"
            llm_provider: LLM提供商，可选 "openai", "ollama"
            embedding_model: 嵌入模型类型
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
            top_k: 检索返回的文档数
            verbose: 是否输出详细日志
        """
        self.vector_store_type = vector_store_type
        self.llm_provider = llm_provider
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.verbose = verbose
        
        # 初始化各组件
        self.embeddings = self._init_embeddings()
        self.llm = self._init_llm()
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None
        
        # 日志级别
        if verbose:
            logging.basicConfig(level=logging.INFO)
    
    def _init_embeddings(self):
        """初始化嵌入模型"""
        if self.embedding_model == "openai":
            return OpenAIEmbeddings()
        elif self.embedding_model == "sentence-transformers":
            from langchain_community.embeddings import SentenceTransformerEmbeddings
            return SentenceTransformerEmbeddings(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
        elif self.embedding_model == "bge":
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5"
            )
        else:
            return OpenAIEmbeddings()
    
    def _init_llm(self):
        """初始化大语言模型"""
        if self.llm_provider == "openai":
            return ChatOpenAI(
                model_name="gpt-5.4-mini",
                temperature=0,
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
        elif self.llm_provider == "ollama":
            return Ollama(
                base_url="http://localhost:11434",
                model="llama3.3",
                temperature=0
            )
        else:
            return ChatOpenAI(temperature=0)
    
    def load_and_process_documents(
        self,
        docs_dir: str,
        extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """加载并处理文档
        
        步骤：加载 -> 分块 -> 向量化 -> 存储
        
        参数:
            docs_dir: 文档目录
            extensions: 要加载的文件扩展名
        返回:
            处理后的文档块列表
        """
        logger.info(f"开始处理文档目录: {docs_dir}")
        
        # 1. 加载文档
        loader = UnifiedDocumentLoader()
        documents = loader.load_directory(docs_dir)
        
        if not documents:
            logger.warning("未找到任何文档")
            return []
        
        logger.info(f"加载了 {len(documents)} 个原始文档")
        
        # 2. 文本分块
        splitter = RecursiveTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_documents(documents)
        
        logger.info(f"分割得到 {len(chunks)} 个文本块")
        
        # 3. 构建向量存储
        if self.vector_store_type == "faiss":
            vector_store = FAISSVectorStore.create_from_documents(
                documents=chunks,
                embeddings=self.embeddings,
                index_path=str(Config.FAISS_INDEX_PATH)
            )
        else:  # chroma
            vector_store = ChromaVectorStore.create_from_documents(
                documents=chunks,
                embeddings=self.embeddings,
                persist_directory=str(Config.CHROMA_DB_PATH)
            )
        
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever(k=self.top_k)
        
        logger.info("向量存储构建完成")
        
        return chunks
    
    def load_vector_store(self) -> bool:
        """加载已存在的向量存储
        
        返回:
            是否加载成功
        """
        if self.vector_store_type == "faiss":
            self.vector_store = FAISSVectorStore(
                embeddings=self.embeddings,
                index_path=str(Config.FAISS_INDEX_PATH)
            )
        else:
            self.vector_store = ChromaVectorStore(
                embeddings=self.embeddings,
                persist_directory=str(Config.CHROMA_DB_PATH)
            )
        
        if self.vector_store.vector_store is None:
            return False
        
        self.retriever = self.vector_store.as_retriever(k=self.top_k)
        logger.info("向量存储加载成功")
        return True
    
    def setup_qa_chain(
        self,
        chain_type: str = "stuff",
        prompt_template: Optional[str] = None,
        return_source_documents: bool = True
    ):
        """设置问答链
        
        参数:
            chain_type: 链类型，可选 "stuff", "map_reduce", "refine"
            prompt_template: 自定义提示词模板
            return_source_documents: 是否返回源文档
        """
        if not self.retriever:
            raise ValueError("请先加载或构建向量存储")
        
        # 自定义提示词
        if prompt_template:
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
        else:
            # 默认提示词
            prompt = PromptTemplate(
                template="""基于以下参考文档回答问题。如果文档中没有相关信息，请说明无法从文档中找到答案。

参考文档：
{context}

问题：{question}

回答：""",
                input_variables=["context", "question"]
            )
        
        # 创建问答链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type=chain_type,
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=return_source_documents,
            verbose=self.verbose
        )
        
        logger.info(f"问答链创建完成 (类型: {chain_type})")
    
    def query(
        self,
        question: str,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """执行问答查询
        
        参数:
            question: 用户问题
            return_sources: 是否返回源文档
        返回:
            包含答案和源文档的字典
        """
        if not self.qa_chain:
            self.setup_qa_chain()
        
        logger.info(f"查询: {question}")
        
        result = self.qa_chain.invoke({"query": question})
        
        response = {
            "answer": result["result"]
        }
        
        if return_sources and "source_documents" in result:
            response["sources"] = [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]
        
        return response
    
    def query_with_conversation(
        self,
        question: str,
        chat_history: List[tuple] = None
    ) -> Dict[str, Any]:
        """带对话历史的查询
        
        适用于多轮对话场景
        
        参数:
            question: 当前问题
            chat_history: 对话历史 [(问题, 回答), ...]
        返回:
            响应字典
        """
        from langchain.chains import ConversationalRetrievalChain  # 旧版链式API，仅作演示
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        if chat_history is None:
            chat_history = []
        
        # 使用对话检索链
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True,
            verbose=self.verbose
        )
        
        result = qa_chain.invoke({
            "question": question,
            "chat_history": chat_history
        })
        
        return {
            "answer": result["answer"],
            "sources": [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in result.get("source_documents", [])
            ]
        }


# 使用示例
if __name__ == "__main__":
    import os
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    
    # 初始化配置
    Config.init_dirs()
    
    # 创建RAG管道
    rag = RAGPipeline(
        vector_store_type="faiss",
        llm_provider="openai",
        chunk_size=500,
        chunk_overlap=100,
        top_k=3,
        verbose=True
    )
    
    # 构建知识库（首次运行）
    # chunks = rag.load_and_process_documents("./data/docs")
    
    # 加载已有知识库
    if rag.load_vector_store():
        # 设置问答链
        rag.setup_qa_chain()
        
        # 查询
        result = rag.query("什么是人工智能？")
        
        print("\n答案:", result["answer"])
        print("\n参考来源:", result.get("sources", []))
