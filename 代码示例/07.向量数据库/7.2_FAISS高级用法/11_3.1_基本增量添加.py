import faiss
import numpy as np
import time

class IncrementalFAISS:
    """增量FAISS索引管理器"""
    
    def __init__(self, d, index_type='Flat'):
        self.d = d
        self.index_type = index_type
        
        if index_type == 'Flat':
            self.index = faiss.IndexFlatL2(d)
        elif index_type == 'IVF':
            # IVF需要预定义nlist
            quantizer = faiss.IndexFlatL2(d)
            self.index = faiss.IndexIVFFlat(quantizer, d, 100)
        elif index_type == 'HNSW':
            self.index = faiss.IndexHNSWFlat(d, 32)
        
        # ID映射：FAISS内部索引 -> 外部ID
        self.id_map = {}
        self.next_id = 0
        
    def add(self, vectors, external_ids=None):
        """添加向量"""
        vectors = np.asarray(vectors, dtype='float32')
        n = len(vectors)
        
        if external_ids is None:
            external_ids = range(self.next_id, self.next_id + n)
        
        # 记录ID映射
        for i, ext_id in enumerate(external_ids):
            self.id_map[self.next_id + i] = ext_id
        
        self.index.add(vectors)
        self.next_id += n
        
    def search(self, query, k=10):
        """搜索并返回外部ID"""
        query = np.asarray(query, dtype='float32').reshape(1, -1)
        D, I = self.index.search(query, k)
        
        # 转换为外部ID
        results = []
        for i, (distances, indices) in enumerate(zip(D, I)):
            hits = []
            for d, idx in zip(distances, indices):
                if idx >= 0 and idx in self.id_map:
                    hits.append({
                        'id': self.id_map[idx],
                        'distance': float(d)
                    })
            results.append(hits)
        
        return results
    
    def get_vector_count(self):
        """获取向量总数"""
        return self.index.ntotal

# 使用示例
manager = IncrementalFAISS(d=128, index_type='HNSW')

# 模拟增量添加
print("增量添加向量...")
for batch in range(10):
    batch_vectors = np.random.random((1000, 128)).astype('float32')
    manager.add(batch_vectors)
    print(f"  已添加: {manager.get_vector_count()} 个向量")

# 搜索
query = np.random.random(128).astype('float32')
results = manager.search(query, k=5)
print("\n搜索结果:", results)
