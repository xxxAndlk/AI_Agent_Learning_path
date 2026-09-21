import numpy as np
class MultiLevelRetriever:
    """多级检索器"""
    
    def __init__(
        self,
        coarse_model: str = "all-MiniLM-L6-v2",
        fine_model: str = "all-mpnet-base-v2",
        coarse_top_k: int = 50,
        final_top_k: int = 5
    ):
        """
        初始化多级检索器
        
        参数:
            coarse_model: 粗排模型（轻量快速）
            fine_model: 精排模型（高精度）
            coarse_top_k: 粗排返回数量
            final_top_k: 最终返回数量
        """
        from sentence_transformers import SentenceTransformer
        
        self.coarse_model = SentenceTransformer(coarse_model)
        self.fine_model = SentenceTransformer(fine_model)
        self.coarse_top_k = coarse_top_k
        self.final_top_k = final_top_k
        
        self.documents = []
        self.doc_embeddings = None
    
    def index_documents(self, documents: List[str]):
        """索引文档"""
        self.documents = documents
        # 使用粗排模型生成嵌入
        self.doc_embeddings = self.coarse_model.encode(
            documents,
            show_progress_bar=True
        )
    
    def retrieve(self, query: str) -> List[Dict]:
        """
        执行多级检索
        
        参数:
            query: 用户查询
        
        返回:
            最终结果列表
        """
        # 第一级：粗排
        query_embedding = self.coarse_model.encode([query])
        coarse_scores = np.dot(
            self.doc_embeddings,
            query_embedding.T
        ).flatten()
        
        # 获取粗排Top-K
        coarse_indices = coarse_scores.argsort()[::-1][:self.coarse_top_k]
        coarse_candidates = [
            self.documents[i] for i in coarse_indices
        ]
        
        # 第二级：精排
        if len(coarse_candidates) <= self.final_top_k:
            return [(doc, 1.0) for doc in coarse_candidates]
        
        candidate_embeddings = self.fine_model.encode(coarse_candidates)
        fine_query_embedding = self.fine_model.encode([query])
        
        fine_scores = np.dot(
            candidate_embeddings,
            fine_query_embedding.T
        ).flatten()
        
        # 获取精排最终结果
        final_indices = fine_scores.argsort()[::-1][:self.final_top_k]
        
        results = [
            (coarse_candidates[i], fine_scores[i])
            for i in final_indices
        ]
        
        return results
