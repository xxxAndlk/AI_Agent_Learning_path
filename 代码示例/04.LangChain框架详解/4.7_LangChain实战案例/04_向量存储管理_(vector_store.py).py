"""
向量存储模块
管理文档的向量嵌入和存储
"""
import logging
from pathlib import Path
from typing import List, Optional, Union, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(
        self,
        persist_directory: str = "./storage/chroma",
        embedding_model: str = "text-embedding-3-small",
        collection_name: str = "documents",
    ):
        """
        初始化向量存储管理器
        
        Args:
            persist_directory: 持久化目录
            embedding_model: 嵌入模型名称
            collection_name: 集合名称
        """
        self.persist_directory = Path(persist_directory)
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.embeddings = None
        self.vector_store = None
        
        # 确保目录存在
        self.persist_directory.mkdir(parents=True, exist_ok=True)
    
    def initialize_embeddings(self, api_key: Optional[str] = None):
        """初始化嵌入模型"""
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            api_key=api_key,
        )
        logger.info(f"初始化嵌入模型: {self.embedding_model}")
    
    def create_vector_store(
        self,
        documents: List[Document],
        force_recreate: bool = False,
    ) -> Chroma:
        """
        创建向量存储
        
        Args:
            documents: 文档列表
            force_recreate: 是否强制重建
            
        Returns:
            Chroma 向量存储对象
        """
        if self.embeddings is None:
            self.initialize_embeddings()
        
        # 检查是否已有持久化的向量存储
        if (
            not force_recreate 
            and (self.persist_directory / "chroma.sqlite3").exists()
        ):
            logger.info("加载已存在的向量存储")
            self.vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
            )
        else:
            logger.info("创建新的向量存储")
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory),
                collection_name=self.collection_name,
            )
        
        logger.info(
            f"向量存储包含 {self.vector_store._collection.count()} 个文档"
        )
        return self.vector_store
    
    def load_vector_store(
        self,
        api_key: Optional[str] = None,
    ) -> Optional[Chroma]:
        """
        加载已存在的向量存储
        
        Args:
            api_key: API 密钥
            
        Returns:
            Chroma 向量存储对象，如果不存在则返回 None
        """
        if self.embeddings is None:
            self.initialize_embeddings(api_key)
        
        if not (self.persist_directory / "chroma.sqlite3").exists():
            logger.warning("向量存储不存在")
            return None
        
        self.vector_store = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
        )
        
        logger.info(
            f"加载向量存储，包含 {self.vector_store._collection.count()} 个文档"
        )
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        """添加文档到向量存储"""
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        self.vector_store.add_documents(documents)
        logger.info(f"添加了 {len(documents)} 个文档")
    
    def delete_all(self):
        """删除所有文档"""
        if self.vector_store is None:
            return
        
        self.vector_store.delete_collection()
        logger.info("已删除所有文档")
    
    def get_retriever(
        self,
        search_type: str = "similarity",
        k: int = 5,
        score_threshold: Optional[float] = None,
        filter: Optional[dict] = None,
    ):
        """
        获取检索器
        
        Args:
            search_type: 搜索类型 ("similarity", "mmr", "similarity_score_threshold")
            k: 返回的文档数量
            score_threshold: 相似度阈值
            filter: 元数据过滤条件
            
        Returns:
            检索器对象
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        retriever_config = {
            "search_type": search_type,
            "k": k,
        }
        
        if filter:
            retriever_config["filter"] = filter
        
        if score_threshold and search_type == "similarity_score_threshold":
            retriever_config["score_threshold"] = score_threshold
        
        return self.vector_store.as_retriever(**retriever_config)
