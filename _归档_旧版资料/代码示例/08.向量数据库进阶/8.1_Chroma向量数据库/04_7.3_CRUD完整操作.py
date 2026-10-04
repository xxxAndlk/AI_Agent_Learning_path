from typing import List, Dict, Any, Optional, Tuple
import json


class VectorDatabaseCRUD:
    """向量数据库完整的CRUD操作"""
    
    def __init__(self, persist_dir: str = "./crud_demo"):
        import chromadb
        
        self.client = chromadb.PersistentClient(
            path=persist_dir,
        )  # 0.4+版本统一SQLite后端，自动持久化
        self.collection = self.client.get_or_create_collection(
            name="crud_operations"
        )
    
    def create(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """
        创建文档
        
        参数:
            documents: 文档内容列表
            metadatas: 元数据列表
            ids: 文档ID列表（可选，自动生成）
            embeddings: 向量列表（可选，自动计算）
        
        返回:
            生成的文档ID列表
        """
        # 自动生成ID
        if ids is None:
            import time
            ids = [f"doc_{int(time.time() * 1000)}_{i}" 
                   for i in range(len(documents))]
        
        # 元数据默认为空字典
        if metadatas is None:
            metadatas = [{} for _ in documents]
        
        # 添加到集合
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        return ids
    
    def read(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        读取文档
        
        参数:
            ids: 要查询的ID列表
            where: 元数据过滤条件
            limit: 返回数量限制
        
        返回:
            包含文档、元数据、ID的字典
        """
        return self.collection.get(
            ids=ids,
            where=where,
            limit=limit
        )
    
    def update(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> bool:
        """
        更新文档
        
        参数:
            ids: 要更新的文档ID列表
            documents: 新的文档内容
            metadatas: 新的元数据
            embeddings: 新的向量
        
        返回:
            是否更新成功
        """
        try:
            self.collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            return True
        except Exception as e:
            print(f"更新失败: {e}")
            return False
    
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict] = None) -> bool:
        """
        删除文档
        
        参数:
            ids: 要删除的文档ID列表
            where: 元数据过滤条件
        
        返回:
            是否删除成功
        """
        try:
            self.collection.delete(ids=ids, where=where)
            return True
        except Exception as e:
            print(f"删除失败: {e}")
            return False
    
    def search(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None,
        include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        相似性搜索
        
        参数:
            query_text: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
            where_document: 文档内容过滤条件
            include: 返回字段列表
        
        返回:
            查询结果字典
        """
        if include is None:
            include = ["documents", "distances", "metadatas", "ids"]
        
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include
        )
    
    def search_by_vector(
        self,
        query_vector: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """使用向量进行搜索"""
        return self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=where
        )


# 使用CRUD操作
def demo_crud():
    """CRUD操作演示"""
    db = VectorDatabaseCRUD("./crud_demo")
    
    # Create - 创建文档
    doc_ids = db.create(
        documents=[
            "深度学习是机器学习的一个分支",
            "自然语言处理研究计算机对语言的理解",
            "计算机视觉让机器看懂图像"
        ],
        metadatas=[
            {"category": "DL", "source": "book"},
            {"category": "NLP", "source": "paper"},
            {"category": "CV", "source": "article"}
        ]
    )
    print(f"创建文档: {doc_ids}")
    
    # Read - 读取文档
    docs = db.read(ids=doc_ids[:2])
    print(f"读取文档: {docs['documents']}")
    
    # Update - 更新文档
    db.update(
        ids=[doc_ids[0]],
        documents=["深度学习使用神经网络模型进行特征学习"],
        metadatas=[{"category": "DL", "source": "updated_book"}]
    )
    print("文档已更新")
    
    # Search - 搜索
    results = db.search("神经网络", n_results=2, where={"category": "DL"})
    print(f"搜索结果: {results['documents']}")
    
    # Delete - 删除
    db.delete(ids=[doc_ids[-1]])
    print(f"删除后数量: {db.collection.count()}")


demo_crud()
