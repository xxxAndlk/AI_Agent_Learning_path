import faiss
import numpy as np
from typing import Dict, List, Any
import json

class MetadataVectorStore:
    """带元数据的向量存储"""
    
    def __init__(self, d: int, index_type: str = "flat"):
        self.d = d
        self.index_type = index_type
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.id_to_idx: Dict[int, int] = {}
        
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict]):
        """
        添加向量和元数据
        
        参数:
            vectors: 向量数组 (n, d)
            metadata: 元数据列表，长度为n
        """
        vectors = vectors.astype('float32')
        
        if self.index is None:
            self._create_index(vectors.shape[0])
        
        # 构建索引
        start_idx = self.index.ntotal
        self.index.add(vectors)
        
        # 记录元数据
        for i, meta in enumerate(metadata):
            self.metadata.append(meta)
            # 假设元数据包含id字段
            if 'id' in meta:
                self.id_to_idx[meta['id']] = start_idx + i
    
    def _create_index(self, nb: int):
        """创建索引"""
        if self.index_type == "flat":
            self.index = faiss.IndexFlatL2(self.d)
        elif self.index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(self.d, 32)
        # 可以添加更多索引类型
    
    def search(self, query: np.ndarray, k: int = 10) -> List[Dict]:
        """
        搜索并返回带元数据的结果
        
        参数:
            query: 查询向量
            k: 返回数量
            
        返回:
            包含元数据的搜索结果列表
        """
        query = query.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                results.append({
                    'rank': i + 1,
                    'distance': float(distances[0][i]),
                    'index': int(idx),
                    'metadata': self.metadata[idx]
                })
        
        return results


# 使用示例
if __name__ == "__main__":
    # 模拟文档向量存储场景
    d = 128
    documents = [
        {"id": 1, "title": "Python教程", "content": "学习Python编程"},
        {"id": 2, "title": "Java教程", "content": "学习Java编程"},
        {"id": 3, "title": "机器学习", "content": "机器学习基础"},
        {"id": 4, "title": "深度学习", "content": "深度学习神经网络"},
        {"id": 5, "title": "Web开发", "content": "Web前端后端开发"},
    ]
    
    # 生成文档向量
    np.random.seed(42)
    vectors = np.random.random((len(documents), d)).astype('float32')
    
    # 创建存储
    store = MetadataVectorStore(d, "hnsw")
    store.add_vectors(vectors, documents)
    
    # 搜索
    query = np.random.random(d).astype('float32')
    results = store.search(query, k=3)
    
    print("=" * 60)
    print("搜索结果")
    print("=" * 60)
    for result in results:
        print(f"\n排名: {result['rank']}")
        print(f"距离: {result['distance']:.4f}")
        print(f"文档: {result['metadata']['title']}")
        print(f"内容: {result['metadata']['content']}")
