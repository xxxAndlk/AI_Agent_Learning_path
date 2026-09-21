import faiss
import numpy as np

class BatchIVFIndex:
    """支持批量重建的IVF索引"""
    
    def __init__(self, d, nlist, batch_size=100000):
        self.d = d
        self.nlist = nlist
        self.batch_size = batch_size
        
        # 临时存储
        self.pending_vectors = []
        
        # 主索引
        self.quantizer = faiss.IndexFlatL2(d)
        self.index = faiss.IndexIVFFlat(self.quantizer, d, nlist)
        
    def add(self, vectors):
        """添加向量到待处理队列"""
        vectors = np.asarray(vectors, dtype='float32')
        self.pending_vectors.append(vectors)
        
        # 达到批量大小时重建索引
        total = sum(len(v) for v in self.pending_vectors)
        if total >= self.batch_size:
            self._rebuild_index()
            
    def _rebuild_index(self):
        """重建索引"""
        if not self.pending_vectors:
            return
            
        print(f"重建索引，累积向量: {sum(len(v) for v in self.pending_vectors)}")
        
        # 合并所有待处理向量
        all_vectors = np.vstack(self.pending_vectors)
        self.pending_vectors = []
        
        # 重建索引
        self.quantizer = faiss.IndexFlatL2(self.d)
        self.index = faiss.IndexIVFFlat(self.quantizer, self.d, self.nlist)
        
        self.index.train(all_vectors)
        self.index.add(all_vectors)
        
    def search(self, query, k=10):
        """搜索"""
        # 确保索引是最新的
        if self.pending_vectors:
            self._rebuild_index()
            
        query = np.asarray(query, dtype='float32').reshape(1, -1)
        return self.index.search(query, k)

# 使用示例
index = BatchIVFIndex(d=128, nlist=100, batch_size=50000)

# 模拟持续添加
for i in range(20):
    batch = np.random.random((3000, 128)).astype('float32')
    index.add(batch)
    
total = sum(len(v) for v in index.pending_vectors) + index.index.ntotal
print(f"当前索引向量数: {index.index.ntotal}, 待处理: {total - index.index.ntotal}")
