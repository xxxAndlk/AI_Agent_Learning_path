class HybridRetriever:
    """混合检索器"""
    
    def __init__(
        self,
        vector_store,
        keyword_retriever,
        vector_weight: float = 0.5,
        keyword_weight: float = 0.5
    ):
        """
        初始化混合检索器
        
        参数:
            vector_store: 向量存储
            keyword_retriever: 关键词检索器
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
        """
        self.vector_store = vector_store
        self.keyword_retriever = keyword_retriever
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        执行混合检索
        
        参数:
            query: 用户查询
            top_k: 返回结果数量
        
        返回:
            融合后的结果列表
        """
        # 执行向量检索
        vector_results = self.vector_store.similarity_search_with_score(
            query, k=top_k * 2
        )
        
        # 执行关键词检索
        keyword_results = self.keyword_retriever.retrieve(query, top_k * 2)
        
        # 归一化分数
        vector_scores = self._normalize_scores([
            score for _, score in vector_results
        ])
        keyword_scores = self._normalize_scores([
            score for _, score in keyword_results
        ])
        
        # 构建结果映射
        result_map = {}
        
        # 添加向量检索结果
        for (doc, score), norm_score in zip(vector_results, vector_scores):
            doc_id = doc.page_content[:50]  # 使用前50字符作为ID
            result_map[doc_id] = {
                'document': doc,
                'vector_score': norm_score,
                'keyword_score': 0.0
            }
        
        # 添加关键词检索结果
        for (content, score), norm_score in zip(keyword_results, keyword_scores):
            doc_id = content[:50]
            if doc_id in result_map:
                result_map[doc_id]['keyword_score'] = norm_score
            else:
                result_map[doc_id] = {
                    'document': None,
                    'vector_score': 0.0,
                    'keyword_score': norm_score
                }
        
        # 计算融合分数
        results = []
        for doc_id, scores in result_map.items():
            fused_score = (
                self.vector_weight * scores['vector_score'] +
                self.keyword_weight * scores['keyword_score']
            )
            results.append({
                'document': scores['document'],
                'score': fused_score,
                'vector_score': scores['vector_score'],
                'keyword_score': scores['keyword_score']
            })
        
        # 排序并返回Top-K
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """归一化分数到0-1范围"""
        if not scores:
            return []
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            return [1.0] * len(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores]
