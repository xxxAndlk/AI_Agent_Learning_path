"""
Chroma持久化配置和数据管理
"""

import chromadb
import os
import shutil


class PersistentVectorDB:
    """持久化向量数据库管理"""
    
    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        
        # 配置持久化（0.4+版本统一SQLite后端，替代Client+Settings）
        self.client = chromadb.PersistentClient(
            path=db_path,
        )  # 禁用遥测等配置项已随旧Settings写法移除
    
    def backup(self, backup_path: str):
        """备份数据库"""
        if os.path.exists(self.db_path):
            shutil.copytree(self.db_path, backup_path)
            print(f"数据库已备份到: {backup_path}")
    
    def restore(self, backup_path: str):
        """恢复数据库"""
        if os.path.exists(backup_path):
            # 删除现有数据
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            shutil.copytree(backup_path, self.db_path)
            print(f"数据库已从 {backup_path} 恢复")
    
    def get_size(self) -> str:
        """获取数据库大小"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.db_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        
        # 转换为人类可读格式
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.2f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.2f} TB"
    
    def cleanup(self, collection_name: str = None):
        """清理数据"""
        if collection_name:
            self.client.delete_collection(collection_name)
            print(f"集合 {collection_name} 已删除")
        else:
            # 删除所有集合
            for col in self.client.list_collections():
                self.client.delete_collection(col.name)
            print("所有集合已删除")


def performance_optimization():
    """性能优化技巧"""
    
    client = chromadb.PersistentClient(
        path="./opt_demo"
    )
    
    collection = client.get_or_create_collection(
        name="optimized"
    )
    
    # ============ 1. 批量操作 ============
    # 一次性添加大量文档比逐个添加快得多
    large_batch = [f"文档{i}" for i in range(1000)]
    large_batch_ids = [f"doc{i}" for i in range(1000)]
    
    # 批量添加（推荐）
    collection.add(
        documents=large_batch,
        ids=large_batch_ids
    )
    
    # ============ 2. 预计算向量 ============
    # 如果有大量文档需要添加，可以预先计算好向量
    import numpy as np
    
    precomputed_vectors = [
        np.random.rand(384).tolist()  # 假设使用MiniLM模型
        for _ in range(1000)
    ]
    
    collection2 = client.get_or_create_collection(
        name="precomputed"
    )
    collection2.add(
        documents=large_batch[:100],
        ids=large_batch_ids[:100],
        embeddings=precomputed_vectors[:100]
    )
    
    # ============ 3. 合理设置查询数量 ============
    # 只请求需要的字段，减少数据传输
    results = collection.query(
        query_texts=["测试查询"],
        n_results=10,
        include=["documents"]  # 只返回文档内容，不返回向量和距离
    )
    
    # ============ 4. 使用合适的过滤条件 ============
    # 在查询时使用where条件缩小搜索范围
    results = collection.query(
        query_texts=["技术文档"],
        n_results=5,
        where={"category": "技术"}  # 先过滤再搜索
    )
    
    # ============ 5. 索引优化 ============
    # 定期检查和优化集合
    print(f"集合文档数量: {collection.count()}")
    print("性能优化完成")


# 运行持久化和优化示例
db_manager = PersistentVectorDB("./my_vector_db")
print("数据库大小:", db_manager.get_size())
performance_optimization()


def production_deployment():
    """生产环境部署配置"""
    
    # ============ 生产环境推荐配置 ============
    
    # 1. 使用PostgreSQL后端（新版chromadb已移除chroma_db_impl后端选项，
    #    生产环境建议部署独立Chroma服务端，或选用PGVector等专用方案）
    """
    服务端启动: chroma run --host 0.0.0.0 --port 8000 --path ./chroma_server_data
    客户端远程连接:
    client = chromadb.HttpClient(host="localhost", port=8000)
    """
    
    # 2. 大规模数据场景（新版chromadb统一本地SQLite存储，不再提供ClickHouse等后端选项）
    """
    大规模或高并发场景建议部署独立Chroma服务端（支持多客户端并发访问），
    或选用Milvus/PGVector等专用向量数据库方案
    """
    
    # 3. 连接池配置
    """
    PostgreSQL连接池建议：
    - max_connections: 20-50
    - min_connections: 5-10
    """
    
    print("生产环境配置请参考注释代码")


production_deployment()
