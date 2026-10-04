# src/vectorstores/chroma_store.py
# Chroma向量存储
from typing import List, Optional, Dict, Any
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings  # v1.x起OpenAI嵌入迁移至langchain_openai
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging
import shutil

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    """Chroma向量存储封装类
    
    Chroma是一个开源的向量数据库，具有以下特点：
    - 简单易用的API
    - 支持持久化存储
    - 支持元数据过滤
    - 支持多租户
    - 可以作为LangChain的向量存储后端
    """
    
    def __init__(
        self,
        embeddings: Any = None,
        persist_directory: Optional[str] = None,
        collection_name: str = "langchain"
    ):
        """
        参数:
            embeddings: 嵌入模型实例
            persist_directory: 持久化目录路径
            collection_name: 集合名称
        """
        self.embeddings = embeddings
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.vector_store: Optional[Chroma] = None
        
        # 如果指定了路径，尝试加载
        if persist_directory and Path(persist_directory).exists():
            self.load()
    
    @staticmethod
    def create_from_documents(
        documents: List[Document],
        embeddings: Any,
        persist_directory: Optional[str] = None,
        collection_name: str = "langchain"
    ) -> "ChromaVectorStore":
        """从文档列表创建向量存储
        
        参数:
            documents: 文档列表
            embeddings: 嵌入模型
            persist_directory: 持久化目录
            collection_name: 集合名称
        返回:
            ChromaVectorStore实例
        """
        store = ChromaVectorStore(
            embeddings=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        
        logger.info(f"开始创建Chroma索引，文档数: {len(documents)}")
        
        # 创建向量存储
        store.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        
        logger.info("Chroma索引创建完成")
        return store
    
    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加文档到向量存储
        
        参数:
            documents: 要添加的文档列表
            ids: 可选的文档ID列表
        返回:
            添加的文档ID列表
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        logger.info(f"添加 {len(documents)} 个文档")
        
        if ids:
            return self.vector_store.add_documents(documents, ids=ids)
        else:
            return self.vector_store.add_documents(documents)
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> List[Document]:
        """相似度搜索
        
        参数:
            query: 查询文本
            k: 返回的相似文档数量
            filter: 元数据过滤条件（Chroma语法）
            where_document: 文档内容过滤
        返回:
            相似文档列表
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter,
            where_document=where_document
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[tuple]:
        """相似度搜索，返回相似度分数
        
        参数:
            query: 查询文本
            k: 返回数量
            filter: 元数据过滤
        返回:
            (文档, 分数)元组列表
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )
    
    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """最大边际相关性搜索
        
        追求检索结果的多样性
        
        参数:
            query: 查询文本
            k: 最终返回数量
            fetch_k: 初始检索数量
            filter: 元数据过滤
        返回:
            文档列表
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            filter=filter
        )
    
    def as_retriever(
        self,
        search_type: str = "similarity",
        k: int = 4,
        filter: Optional[Dict] = None,
        **kwargs
    ):
        """转换为检索器
        
        参数:
            search_type: 搜索类型
            k: 返回数量
            filter: 元数据过滤
            **kwargs: 其他搜索参数
        返回:
            检索器对象
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k, "filter": filter, **kwargs}
        )
    
    def persist(self) -> None:
        """持久化向量存储到磁盘
        
        Chroma默认会在添加文档时自动持久化
        这个方法用于手动触发持久化
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        logger.info("持久化Chroma数据")
        self.vector_store.persist()
    
    def save(self, path: str = None) -> None:
        """保存向量存储
        
        参数:
            path: 保存路径（Chroma使用persist_directory，无需额外保存）
        """
        # Chroma会自动持久化到指定目录
        # 此方法保留为接口一致性
        if self.vector_store:
            self.persist()
    
    def load(self, path: str = None) -> bool:
        """从磁盘加载向量存储
        
        参数:
            path: 加载路径，为空则使用初始化时的路径
        返回:
            是否加载成功
        """
        path = path or self.persist_directory
        
        if not path:
            raise ValueError("未指定加载路径")
        
        if not Path(path).exists():
            logger.warning(f"索引路径不存在: {path}")
            return False
        
        logger.info(f"从磁盘加载Chroma索引: {path}")
        
        try:
            self.vector_store = Chroma(
                persist_directory=path,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            logger.info("加载成功")
            return True
        except Exception as e:
            logger.error(f"加载失败: {e}")
            return False
    
    def delete(self, path: str = None) -> bool:
        """删除向量存储
        
        参数:
            path: 删除路径
        返回:
            是否删除成功
        """
        path = path or self.persist_directory
        
        if not path:
            return False
        
        try:
            if Path(path).exists():
                shutil.rmtree(path)
                logger.info(f"已删除: {path}")
            self.vector_store = None
            return True
        except Exception as e:
            logger.error(f"删除失败: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息
        
        返回:
            包含统计信息的字典
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        collection = self.vector_store.get()
        
        return {
            "count": len(collection.get("ids", [])),
            "embeddings_dimension": self.vector_store._embedding_function.embed_query("test").__len__() if self.embeddings else None
        }


class ChromaCollectionManager:
    """Chroma集合管理器
    
    提供多集合管理功能
    适用于需要按类别隔离文档的场景
    """
    
    def __init__(
        self,
        embeddings: Any,
        persist_directory: str
    ):
        """
        参数:
            embeddings: 嵌入模型
            persist_directory: 持久化目录
        """
        self.embeddings = embeddings
        self.persist_directory = persist_directory
        self.stores: Dict[str, ChromaVectorStore] = {}
    
    def get_or_create_collection(
        self,
        collection_name: str
    ) -> ChromaVectorStore:
        """获取或创建集合
        
        参数:
            collection_name: 集合名称
        返回:
            ChromaVectorStore实例
        """
        if collection_name not in self.stores:
            self.stores[collection_name] = ChromaVectorStore(
                embeddings=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=collection_name
            )
        
        return self.stores[collection_name]
    
    def list_collections(self) -> List[str]:
        """列出所有集合名称
        
        返回:
            集合名称列表
        """
        # 读取持久化目录中的集合
        if not Path(self.persist_directory).exists():
            return []
        
        # Chroma的集合信息存储在chroma.sqlite
        import sqlite3
        
        db_path = Path(self.persist_directory) / "chroma.sqlite"
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM collections")
        collections = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return collections


# FAISS与Chroma对比
"""
| 特性         | FAISS                  | Chroma                    |
|--------------|------------------------|---------------------------|
| 类型         | 向量检索库             | 向量数据库                 |
| 安装         | pip install faiss-cpu | pip install chromadb     |
| 持久化       | 需要手动保存           | 自动持久化                |
| 元数据过滤   | 不支持                 | 支持                      |
| 多租户       | 不支持                 | 支持                      |
| 分布式       | 不支持                 | 支持（需要服务器版）      |
| 性能         | 快速                   | 中等                      |
| 适用场景     | 小规模数据、科研       | 生产环境、多租户应用       |
"""


# 使用示例
if __name__ == "__main__":
    from src.loaders.directory_loader import UnifiedDocumentLoader
    from src.chunking.recursive_splitter import RecursiveTextSplitter
    
    logging.basicConfig(level=logging.INFO)
    
    # 1. 加载文档
    loader = UnifiedDocumentLoader()
    documents = loader.load_directory("./data/docs")
    
    print(f"加载了 {len(documents)} 个文档")
    
    # 2. 分块
    splitter = RecursiveTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    
    print(f"分割得到 {len(chunks)} 个块")
    
    # 3. 创建Chroma向量存储
    embeddings = OpenAIEmbeddings()
    
    vector_store = ChromaVectorStore.create_from_documents(
        documents=chunks,
        embeddings=embeddings,
        persist_directory="./data/processed/vectorstores/chroma_db",
        collection_name="my_rag_knowledge"
    )
    
    print("Chroma向量存储创建完成")
    
    # 4. 搜索
    results = vector_store.similarity_search("人工智能", k=3)
    
    print(f"\n搜索结果 ({len(results)}个):")
    for i, doc in enumerate(results):
        print(f"--- 结果 {i+1} ---")
        print(doc.page_content[:100])
