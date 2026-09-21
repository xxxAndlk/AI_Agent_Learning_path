import psycopg2
import psycopg2.extras  # Json辅助类在extras子模块，需显式导入
from pgvector.psycopg2 import register_vector
import numpy as np
from typing import List, Tuple, Dict, Any

class PGVectorClient:
    """PGVector客户端封装"""
    
    def __init__(self, connection_string: str = "postgresql://postgres:password@localhost:5432/postgres"):
        """
        初始化PGVector客户端
        
        参数:
            connection_string: PostgreSQL连接字符串
        """
        self.connection_string = connection_string
        self.conn = None
        self._connect()
    
    def _connect(self):
        """建立连接并注册向量类型"""
        self.conn = psycopg2.connect(self.connection_string)
        register_vector(self.conn)
        
        # 启用pgvector扩展
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.conn.commit()
        
        print("[PGVector] 连接成功")
    
    def create_table(self, table_name: str, dimension: int = 1536):
        """
        创建向量表
        
        参数:
            table_name: 表名
            dimension: 向量维度
        """
        with self.conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector({dimension}),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 创建向量索引（HNSW）
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
                ON {table_name} 
                USING hnsw (embedding vector_cosine_ops);
            """)
            
            self.conn.commit()
        
        print(f"[PGVector] 表 {table_name} 创建成功")
    
    def insert_vectors(
        self, 
        table_name: str, 
        contents: List[str], 
        embeddings: List[List[float]],
        metadatas: List[Dict] = None
    ):
        """
        批量插入向量
        
        参数:
            table_name: 表名
            contents: 文本内容列表
            embeddings: 向量列表
            metadatas: 元数据列表（可选）
        """
        if metadatas is None:
            metadatas = [{} for _ in contents]
        
        with self.conn.cursor() as cur:
            for content, embedding, metadata in zip(contents, embeddings, metadatas):
                cur.execute(f"""
                    INSERT INTO {table_name} (content, embedding, metadata)
                    VALUES (%s, %s, %s);
                """, (content, embedding, psycopg2.extras.Json(metadata)))
            
            self.conn.commit()
        
        print(f"[PGVector] 插入 {len(contents)} 条记录")
    
    def search_similar(
        self,
        table_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        metric: str = "cosine"  # cosine, l2, inner_product
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索
        
        参数:
            table_name: 表名
            query_embedding: 查询向量
            top_k: 返回数量
            metric: 距离度量方式
        
        返回:
            搜索结果列表
        """
        # 选择距离函数
        distance_func = {
            "cosine": "1 - (embedding <=> %s::vector)",  # 余弦相似度
            "l2": "embedding <-> %s::vector",           # L2距离
            "inner_product": "embedding <#> %s::vector"  # 内积
        }.get(metric, "1 - (embedding <=> %s::vector)")
        
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, content, metadata, {distance_func} as distance
                FROM {table_name}
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_embedding, query_embedding, top_k))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": row[2],
                    "score": float(row[3]) if metric == "cosine" else float(row[3])
                })
        
        return results
    
    def hybrid_search(
        self,
        table_name: str,
        query_embedding: List[float],
        keyword: str = None,
        filter_conditions: Dict = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        混合搜索：向量相似度 + 关键词匹配 + 过滤条件
        
        参数:
            table_name: 表名
            query_embedding: 查询向量
            keyword: 关键词（全文搜索）
            filter_conditions: 过滤条件
            top_k: 返回数量
        """
        # 构建WHERE子句
        where_clauses = ["1=1"]
        params = [query_embedding]
        
        if keyword:
            where_clauses.append("content ILIKE %s")
            params.append(f"%{keyword}%")
        
        if filter_conditions:
            for key, value in filter_conditions.items():
                where_clauses.append(f"metadata->>{key} = %s")
                params.append(value)
        
        where_sql = " AND ".join(where_clauses)
        params.append(top_k)
        
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, content, metadata, 
                       1 - (embedding <=> %s::vector) as similarity
                FROM {table_name}
                WHERE {where_sql}
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, tuple(params))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": row[2],
                    "similarity": float(row[3])
                })
        
        return results
    
    def delete_by_id(self, table_name: str, doc_id: int):
        """根据ID删除"""
        with self.conn.cursor() as cur:
            cur.execute(f"DELETE FROM {table_name} WHERE id = %s;", (doc_id,))
            self.conn.commit()
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            print("[PGVector] 连接已关闭")


# ============ 使用示例 ============

def pgvector_basic_example():
    """PGVector基础使用示例"""
    
    print("="*60)
    print("PGVector基础示例")
    print("="*60)
    
    # 初始化客户端
    client = PGVectorClient("postgresql://postgres:password@localhost:5432/postgres")
    
    # 创建表
    client.create_table("documents", dimension=384)
    
    # 准备示例数据
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('BAAI/bge-small-zh')
    
    documents = [
        "机器学习是人工智能的一个重要分支",
        "深度学习使用神经网络进行学习",
        "Python是数据科学的主流语言",
        "PostgreSQL是强大的开源数据库",
        "向量数据库用于存储和检索高维向量"
    ]
    
    # 生成向量
    embeddings = model.encode(documents).tolist()
    
    # 元数据
    metadatas = [
        {"category": "AI", "author": "user1"},
        {"category": "AI", "author": "user2"},
        {"category": "Programming", "author": "user1"},
        {"category": "Database", "author": "user3"},
        {"category": "Database", "author": "user2"}
    ]
    
    # 插入数据
    client.insert_vectors("documents", documents, embeddings, metadatas)
    
    # 向量搜索
    query = "人工智能和机器学习"
    query_emb = model.encode(query).tolist()
    
    print(f"\n查询: {query}")
    print("-"*60)
    
    results = client.search_similar("documents", query_emb, top_k=3)
    
    print("\n向量搜索结果:")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['score']:.4f}] {result['content']}")
    
    # 混合搜索
    print("\n" + "="*60)
    print("混合搜索（向量 + 关键词过滤）")
    print("="*60)
    
    results = client.hybrid_search(
        "documents",
        query_emb,
        keyword="学习",  # 包含"学习"关键字
        filter_conditions={"category": "AI"},  # category为AI
        top_k=3
    )
    
    print(f"\n查询: {query} (关键词: 学习, 分类: AI)")
    print("-"*60)
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['similarity']:.4f}] {result['content']}")
        print(f"   元数据: {result['metadata']}")
    
    # 关闭连接
    client.close()


if __name__ == "__main__":
    pgvector_basic_example()
