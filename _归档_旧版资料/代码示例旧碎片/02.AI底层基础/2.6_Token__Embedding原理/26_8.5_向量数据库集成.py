# 与FAISS集成示例（需要安装faiss-cpu或faiss-gpu）
import numpy as np

class VectorDatabase:
    """简化版向量数据库"""
    
    def __init__(self, dimension=768):
        self.dimension = dimension
        self.vectors = []
        self.metadata = []
    
    def add(self, vector, meta=None):
        """添加向量"""
        self.vectors.append(vector)
        self.metadata.append(meta or {})
    
    def search(self, query_vector, top_k=5):
        """搜索最近邻"""
        query = np.array(query_vector)
        vectors = np.array(self.vectors)
        
        # 计算余弦相似度
        similarities = np.dot(vectors, query) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(query)
        )
        
        # 排序
        indices = np.argsort(similarities)[::-1][:top_k]
        return [(self.metadata[i], similarities[i]) for i in indices]

# 实际应用建议使用专业向量库：
# - FAISS: 高性能，适合大规模
# - Milvus: 分布式，支持云部署
# - Pinecone: 托管服务，开箱即用
# - Chroma: 轻量级，适合原型开发
