class VectorRetriever:
    """向量检索器"""
    
    def __init__(self, vector_store, embeddings):
        self.vector_store = vector_store
        self.embeddings = embeddings
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        执行向量检索
        
        参数:
            query: 用户查询
            top_k: 返回结果数量
        
        返回:
            相关文档列表
        """
        # 将查询转换为向量
        query_vector = self.embeddings.embed_query(query)
        
        # 在向量数据库中搜索
        results = self.vector_store.similarity_search_by_vector(
            embedding=query_vector,
            k=top_k
        )
        
        return results
