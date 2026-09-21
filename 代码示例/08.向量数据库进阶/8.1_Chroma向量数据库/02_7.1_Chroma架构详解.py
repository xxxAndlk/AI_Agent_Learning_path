"""
Chroma架构分为三层：
1. API层：提供Python/JS客户端API
2. 核心层：向量存储和检索引擎
3. 持久化层：支持多种后端存储

持久化说明（0.4+版本）：
- 统一使用本地SQLite后端，轻量级
- PersistentClient(path=...)指定持久化目录
- 生产环境部署Chroma服务端，客户端远程连接
"""

import chromadb
from typing import List, Dict, Any, Optional
import os


class ChromaManager:
    """Chroma向量数据库管理器"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_data",
        collection_name: str = "default",
        backend: str = "duckdb+parquet"
    ):
        """
        初始化Chroma管理器
        
        参数:
            persist_directory: 数据持久化目录
            collection_name: 集合名称
            backend: 存储后端类型
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # 创建客户端（0.4+版本统一SQLite后端，替代Client+Settings写法）
        self.client = chromadb.PersistentClient(
            path=persist_directory,
        )  # 数据自动持久化到path目录
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": f"Chroma collection: {collection_name}"}
        )
    
    def reset(self):
        """重置集合，删除所有数据"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }


# 创建管理器实例
manager = ChromaManager(
    persist_directory="./my_vector_db",
    collection_name="knowledge_base",
    backend="duckdb+parquet"
)
print("集合统计:", manager.get_stats())
