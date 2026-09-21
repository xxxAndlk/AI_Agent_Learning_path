"""
大规模向量检索系统架构

组件说明：
1. 数据预处理层：向量归一化、维度验证
2. 索引构建层：根据数据规模选择索引类型
3. 查询处理层：批量查询、结果缓存
4. 监控层：性能指标收集
"""

import faiss
import numpy as np
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """搜索结果"""
    ids: np.ndarray
    distances: np.ndarray
    
@dataclass  
class IndexConfig:
    """索引配置"""
    dim: int
    index_type: str  # 'flat', 'ivf', 'hnsw', 'pq', 'ivf-pq'
    nlist: int = 100
    nprobe: int = 10
    m: int = 8
    nbits: int = 8
    M: int = 16
    efSearch: int = 64

class VectorSearchSystem:
    """大规模向量检索系统"""
    
    def __init__(self, config: IndexConfig):
        self.config = config
        self.index = None
        self._build_index()
        
    def _build_index(self):
        """根据配置构建索引"""
        d = self.config.dim
        
        if self.config.index_type == 'flat':
            self.index = faiss.IndexFlatL2(d)
            
        elif self.config.index_type == 'ivf':
            quantizer = faiss.IndexFlatL2(d)
            self.index = faiss.IndexIVFFlat(
                quantizer, d, self.config.nlist
            )
            # IVF需要标记为未训练
            self.index.is_trained = False
            
        elif self.config.index_type == 'hnsw':
            self.index = faiss.IndexHNSWFlat(d, self.config.M)
            self.index.hnsw.efSearch = self.config.efSearch
            
        elif self.config.index_type == 'pq':
            self.index = faiss.IndexPQ(d, self.config.m, self.config.nbits)
            
        elif self.config.index_type == 'ivf-pq':
            quantizer = faiss.IndexFlatL2(d)
            self.index = faiss.IndexIVFPQ(
                quantizer, d, self.config.nlist,
                self.config.m, self.config.nbits
            )
            self.index.is_trained = False
            
        logger.info(f"创建索引: {self.config.index_type}")
        
    def train(self, vectors: np.ndarray):
        """训练索引"""
        if hasattr(self.index, 'train'):
            logger.info("开始训练索引...")
            start = time.time()
            self.index.train(vectors)
            logger.info(f"训练完成，耗时: {time.time()-start:.2f}s")
            
    def add(self, vectors: np.ndarray, batch_size: int = 100000):
        """批量添加向量"""
        vectors = np.asarray(vectors, dtype='float32')
        n = len(vectors)
        
        logger.info(f"添加 {n} 个向量...")
        start = time.time()
        
        if n <= batch_size:
            self.index.add(vectors)
        else:
            # 分批添加
            for i in range(0, n, batch_size):
                batch = vectors[i:i+batch_size]
                self.index.add(batch)
                logger.info(f"  已添加 {min(i+batch_size, n)}/{n}")
        
        logger.info(f"添加完成，耗时: {time.time()-start:.2f}s")
        
    def search(
        self, 
        query: np.ndarray, 
        k: int = 10,
        nprobe: Optional[int] = None
    ) -> SearchResult:
        """搜索"""
        query = np.asarray(query, dtype='float32')
        
        # IVF类型支持动态调整nprobe
        if nprobe is not None and hasattr(self.index, 'nprobe'):
            self.index.nprobe = nprobe
            
        D, I = self.index.search(query, k)
        
        return SearchResult(ids=I, distances=D)
    
    def batch_search(
        self,
        queries: np.ndarray,
        k: int = 10,
        nprobe: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """批量搜索"""
        queries = np.asarray(queries, dtype='float32')
        
        if nprobe is not None and hasattr(self.index, 'nprobe'):
            self.index.nprobe = nprobe
            
        return self.index.search(queries, k)
    
    def get_stats(self) -> dict:
        """获取索引统计信息"""
        return {
            'total_vectors': self.index.ntotal,
            'dim': self.config.dim,
            'index_type': self.config.index_type,
        }
