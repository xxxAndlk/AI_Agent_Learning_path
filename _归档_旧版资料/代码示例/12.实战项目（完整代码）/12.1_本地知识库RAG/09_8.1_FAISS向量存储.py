# src/vectorstores/faiss_store.py
# FAISS向量存储
from typing import List, Optional, Dict, Any
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings  # v1.x起OpenAI嵌入迁移至langchain_openai
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging
import pickle

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """FAISS向量存储封装类
    
    提供完整的向量存储、检索、持久化功能
    支持多种嵌入模型
    """
    
    def __init__(
        self,
        embeddings: Any = None,
        index_path: Optional[str] = None,
        distance_metric: str = "cosine"
    ):
        """
        参数:
            embeddings: 嵌入模型实例
            index_path: FAISS索引保存路径
            distance_metric: 距离度量方式，可选 "cosine", "euclidean", "manhattan"
        """
        self.embeddings = embeddings
        self.index_path = index_path
        self.distance_metric = distance_metric
        self.vector_store: Optional[FAISS] = None
        
        # 如果指定了路径，尝试加载
        if index_path and Path(index_path).exists():
            self.load()
    
    @staticmethod
    def create_from_documents(
        documents: List[Document],
        embeddings: Any,
        index_path: Optional[str] = None,
        distance_metric: str = "cosine"
    ) -> "FAISSVectorStore":
        """从文档列表创建向量存储
        
        参数:
            documents: 文档列表
            embeddings: 嵌入模型
            index_path: 保存路径
            distance_metric: 距离度量
        返回:
            FAISSVectorStore实例
        """
        store = FAISSVectorStore(
            embeddings=embeddings,
            index_path=index_path,
            distance_metric=distance_metric
        )
        
        logger.info(f"开始创建FAISS索引，文档数: {len(documents)}")
        
        # 创建向量存储
        store.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embeddings
        )
        
        # 保存到磁盘
        if index_path:
            store.save(index_path)
        
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
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """相似度搜索
        
        参数:
            query: 查询文本
            k: 返回的相似文档数量
            filter: 可选的元数据过滤条件
        返回:
            相似文档列表
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter
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
    
    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """通过向量进行搜索
        
        参数:
            embedding: 查询向量
            k: 返回数量
            filter: 元数据过滤
        返回:
            相似文档列表
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.similarity_search_by_vector(
            embedding=embedding,
            k=k,
            filter=filter
        )
    
    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Document]:
        """最大边际相关性搜索
        
        追求检索结果的多样性，避免返回高度相似的文档
        
        参数:
            query: 查询文本
            k: 最终返回数量
            fetch_k: 初始检索数量
            lambda_mult: 多样性-相关性平衡因子
        返回:
            文档列表
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult
        )
    
    def as_retriever(
        self,
        search_type: str = "similarity",
        k: int = 4,
        **kwargs
    ):
        """转换为检索器
        
        参数:
            search_type: 搜索类型，可选 "similarity", "mmr", "similarity_score_threshold"
            k: 返回数量
            **kwargs: 其他搜索参数
        返回:
            检索器对象
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k, **kwargs}
        )
    
    def save(self, path: str) -> None:
        """保存向量存储到磁盘
        
        参数:
            path: 保存路径
        """
        if self.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        logger.info(f"保存FAISS索引到: {path}")
        
        # 创建目录
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # 保存
        self.vector_store.save_local(path)
        
        logger.info("保存完成")
    
    def load(self, path: str = None) -> bool:
        """从磁盘加载向量存储
        
        参数:
            path: 加载路径，为空则使用初始化时的路径
        返回:
            是否加载成功
        """
        path = path or self.index_path
        
        if not path:
            raise ValueError("未指定加载路径")
        
        if not Path(path).exists():
            logger.warning(f"索引路径不存在: {path}")
            return False
        
        logger.info(f"从磁盘加载FAISS索引: {path}")
        
        try:
            self.vector_store = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("加载成功")
            return True
        except Exception as e:
            logger.error(f"加载失败: {e}")
            return False
    
    def merge_from(self, other: "FAISSVectorStore") -> None:
        """合并另一个向量存储
        
        参数:
            other: 另一个FAISSVectorStore实例
        """
        if self.vector_store is None or other.vector_store is None:
            raise ValueError("向量存储未初始化")
        
        logger.info("开始合并向量存储")
        self.vector_store.merge_from(other.vector_store)
        logger.info("合并完成")
    
    def delete(self, path: str = None) -> bool:
        """删除向量存储
        
        参数:
            path: 删除路径，为空则使用初始化时的路径
        返回:
            是否删除成功
        """
        import shutil
        
        path = path or self.index_path
        
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


class FAISSIndexBuilder:
    """FAISS索引构建器
    
    提供多种索引类型的构建方法
    优化大规模数据的索引效率
    """
    
    @staticmethod
    def build_flat_index(
        documents: List[Document],
        embeddings: Any,
        normalize_L2: bool = True
    ) -> FAISS:
        """构建Flat索引
        
        最简单精确的索引，适合小数据集
        """
        logger.info("构建Flat索引")
        
        return FAISS.from_documents(
            documents=documents,
            embedding=embeddings
        )
    
    @staticmethod
    def build_ivf_index(
        documents: List[Document],
        embeddings: Any,
        nlist: int = 100,
        nprobe: int = 10
    ) -> FAISS:
        """构建IVF索引
        
        倒排索引，适合大数据集
        先聚类，搜索时只搜索最近的几个类
        
        参数:
            nlist: 聚类数量
            nprobe: 搜索的聚类数量
        """
        # 注意：LangChain的FAISS封装暂不支持直接创建IVF
        # 这里使用Flat索引作为替代
        # 实际生产环境可以使用faiss直接创建
        logger.info(f"构建IVF索引 (nlist={nlist}, nprobe={nprobe})")
        
        vs = FAISS.from_documents(documents, embeddings)
        
        # 可以通过faiss.IndexIVF来优化
        # 实际实现需要直接操作faiss包
        
        return vs
    
    @staticmethod
    def build_hnsw_index(
        documents: List[Document],
        embeddings: Any,
        M: int = 32,
        efConstruction: int = 200
    ) -> FAISS:
        """构建HNSW索引
        
        层级导航小世界图索引
        高速搜索，适合高维数据
        
        参数:
            M: 每个节点的边数
            efConstruction: 构建时的搜索宽度
        """
        logger.info(f"构建HNSW索引 (M={M}, efConstruction={efConstruction})")
        
        # LangChain FAISS不支持直接创建HNSW
        # 使用标准索引
        return FAISS.from_documents(documents, embeddings)


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
    
    # 3. 创建向量存储
    embeddings = OpenAIEmbeddings()
    
    vector_store = FAISSVectorStore.create_from_documents(
        documents=chunks,
        embeddings=embeddings,
        index_path="./data/processed/vectorstores/faiss_index"
    )
    
    print("向量存储创建完成")
    
    # 4. 搜索
    results = vector_store.similarity_search("人工智能", k=3)
    
    print(f"\n搜索结果 ({len(results)}个):")
    for i, doc in enumerate(results):
        print(f"--- 结果 {i+1} ---")
        print(doc.page_content[:100])
