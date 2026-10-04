from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    """交叉编码器重排序器"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        初始化重排序器
        
        参数:
            model_name: 交叉编码器模型名称
        """
        self.model = CrossEncoder(model_name)
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        重排序文档
        
        参数:
            query: 用户查询
            documents: 文档列表
            top_k: 返回结果数量
        
        返回:
            重排序后的结果
        """
        # 构建查询-文档对
        pairs = [(query, doc) for doc in documents]
        
        # 获取相关性分数
        scores = self.model.predict(pairs)
        
        # 按分数排序
        results = [
            {'document': doc, 'score': float(score)}
            for doc, score in zip(documents, scores)
        ]
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
