import faiss
import numpy as np
import time
from typing import List, Tuple

class VectorSearchEngine:
    """向量搜索引擎封装类"""
    
    def __init__(self, d: int, index_type: str = "flat"):
        """
        初始化搜索引擎
        
        参数:
            d: 向量维度
            index_type: 索引类型 ('flat', 'ivf', 'hnsw', 'ivf_pq')
        """
        self.d = d
        self.index_type = index_type
        self.index = None
        
    def build_index(self, vectors: np.ndarray, nlist: int = 100, 
                    M: int = 32, efSearch: int = 16):
        """
        构建索引
        
        参数:
            vectors: 原始向量数据，形状为 (n, d)
            nlist: IVF聚类数量
            M: HNSW连接数
            efSearch: HNSW搜索宽度
        """
        vectors = self._preprocess(vectors)
        
        if self.index_type == "flat":
            self.index = faiss.IndexFlatL2(self.d)
            self.index.add(vectors)
            
        elif self.index_type == "ivf":
            quantizer = faiss.IndexFlatL2(self.d)
            self.index = faiss.IndexIVFFlat(quantizer, self.d, nlist)
            self.index.train(vectors)
            self.index.add(vectors)
            
        elif self.index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(self.d, M)
            self.index.hnsw.efSearch = efSearch
            self.index.add(vectors)
            
        elif self.index_type == "ivf_pq":
            quantizer = faiss.IndexFlatL2(self.d)
            m = 8  # PQ子向量数
            nbits = 8
            self.index = faiss.IndexIVFPQ(quantizer, self.d, nlist, m, nbits)
            self.index.train(vectors)
            self.index.add(vectors)
            
        else:
            raise ValueError(f"不支持的索引类型: {self.index_type}")
            
        return self
        
    def search(self, query: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        搜索最近邻
        
        参数:
            query: 查询向量，形状为 (nq, d) 或 (d,)
            k: 返回的最近邻数量
            
        返回:
            (distances, indices): 距离矩阵和索引矩阵
        """
        if query.ndim == 1:
            query = query.reshape(1, -1)
        query = self._preprocess(query)
        
        return self.index.search(query, k)
    
    def set_search_params(self, **kwargs):
        """设置搜索参数"""
        if self.index_type == "ivf" or self.index_type == "ivf_pq":
            if 'nprobe' in kwargs:
                self.index.nprobe = kwargs['nprobe']
        elif self.index_type == "hnsw":
            if 'efSearch' in kwargs:
                self.index.hnsw.efSearch = kwargs['efSearch']
    
    def _preprocess(self, vectors: np.ndarray) -> np.ndarray:
        """预处理向量"""
        return vectors.astype('float32')
    
    def get_vector_count(self) -> int:
        """获取索引中的向量数量"""
        return self.index.ntotal if self.index else 0


# 使用示例
if __name__ == "__main__":
    # 配置参数
    d = 128
    nb = 10000
    nq = 5
    k = 5
    
    # 生成测试数据
    np.random.seed(42)
    vectors = np.random.random((nb, d)).astype('float32')
    queries = np.random.random((nq, d)).astype('float32')
    
    # 测试不同索引类型
    index_types = ["flat", "ivf", "hnsw", "ivf_pq"]
    
    print("=" * 70)
    print("向量搜索引擎性能对比")
    print("=" * 70)
    
    for index_type in index_types:
        print(f"\n索引类型: {index_type.upper()}")
        print("-" * 50)
        
        # 创建并构建索引
        engine = VectorSearchEngine(d, index_type)
        
        if index_type == "ivf":
            engine.build_index(vectors, nlist=100)
            engine.set_search_params(nprobe=10)
        elif index_type == "hnsw":
            engine.build_index(vectors, M=32, efSearch=32)
        elif index_type == "ivf_pq":
            engine.build_index(vectors, nlist=100)
            engine.set_search_params(nprobe=10)
        else:
            engine.build_index(vectors)
        
        # 搜索并计时
        start = time.time()
        D, I = engine.search(queries, k)
        elapsed = time.time() - start
        
        print(f"向量数量: {engine.get_vector_count()}")
        print(f"搜索耗时: {elapsed*1000:.2f}ms")
        print(f"平均单次查询: {elapsed/nq*1000:.2f}ms")
        
        # 显示第一个查询的结果
        print(f"查询0的top-{k}结果: {I[0]}")
