import faiss
import numpy as np
from typing import List, Tuple

class EfficientVectorProcessor:
    """高效的向量处理工具类"""
    
    @staticmethod
    def create_batches(data: np.ndarray, batch_size: int) -> List[np.ndarray]:
        """
        将大数据分批处理
        
        参数:
            data: 完整数据 (n, d)
            batch_size: 批量大小
            
        返回:
            分批后的数据列表
        """
        n = data.shape[0]
        batches = []
        for i in range(0, n, batch_size):
            batches.append(data[i:i+batch_size])
        return batches
    
    @staticmethod
    def batch_add_index(index, vectors: np.ndarray, batch_size: int = 10000):
        """
        分批添加向量到索引
        
        参数:
            index: FAISS索引
            vectors: 向量数据
            batch_size: 批量大小
        """
        batches = EfficientVectorProcessor.create_batches(vectors, batch_size)
        for batch in batches:
            index.add(batch)
    
    @staticmethod
    def batch_search(index, queries: np.ndarray, k: int, 
                     batch_size: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        分批执行搜索
        
        参数:
            index: FAISS索引
            queries: 查询向量
            k: 返回数量
            batch_size: 批量大小
            
        返回:
            (distances, indices)
        """
        nq = queries.shape[0]
        all_distances = np.zeros((nq, k), dtype='float32')
        all_indices = np.full((nq, k), -1, dtype='int64')
        
        for i in range(0, nq, batch_size):
            batch_queries = queries[i:i+batch_size]
            D, I = index.search(batch_queries, k)
            
            end_idx = min(i + batch_size, nq)
            all_distances[i:end_idx] = D
            all_indices[i:end_idx] = I
        
        return all_distances, all_indices


# 性能测试
if __name__ == "__main__":
    d = 128
    nb = 100000
    
    np.random.seed(42)
    vectors = np.random.random((nb, d)).astype('float32')
    queries = np.random.random((5000, d)).astype('float32')
    
    # 测试分批添加
    index = faiss.IndexFlatL2(d)
    
    import time
    start = time.time()
    EfficientVectorProcessor.batch_add_index(index, vectors, batch_size=10000)
    add_time = time.time() - start
    
    print(f"分批添加 {nb} 个向量耗时: {add_time:.2f}秒")
    
    # 测试分批搜索
    start = time.time()
    D, I = EfficientVectorProcessor.batch_search(index, queries, k=10, batch_size=1000)
    search_time = time.time() - start
    
    print(f"分批搜索 {queries.shape[0]} 个查询耗时: {search_time:.2f}秒")
