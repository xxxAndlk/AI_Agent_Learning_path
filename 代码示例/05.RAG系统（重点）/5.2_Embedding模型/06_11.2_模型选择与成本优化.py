class EmbeddingCostOptimizer:
    """Embedding成本优化器"""
    
    # 模型定价（每1000个token）
    PRICING = {
        'text-embedding-3-small': {
            'price_per_1k': 0.00002,  # $0.02 per 1M tokens
            'dimensions': 1536
        },
        'text-embedding-3-large': {
            'price_per_1k': 0.00013,  # $0.13 per 1M tokens
            'dimensions': 3072
        },
        'text-embedding-ada-002': {
            'price_per_1k': 0.0001,  # $0.10 per 1M tokens
            'dimensions': 1536
        }
    }
    
    def __init__(self, model: str = 'text-embedding-3-small'):
        self.model = model
        self.pricing = self.PRICING.get(model, self.PRICING['text-embedding-3-small'])
    
    def estimate_cost(
        self,
        num_texts: int,
        avg_tokens_per_text: int
    ) -> float:
        """
        估算成本
        
        参数:
            num_texts: 文本数量
            avg_tokens_per_text: 每个文本的平均token数
        
        返回:
            预估成本（美元）
        """
        total_tokens = num_texts * avg_tokens_per_text
        total_cost = (total_tokens / 1000) * self.pricing['price_per_1k']
        
        return total_cost
    
    def get_optimal_dimensions(
        self,
        original_dimensions: int,
        target_dimensions: int
    ) -> int:
        """
        获取最优维度
        
        参数:
            original_dimensions: 原始维度
            target_dimensions: 目标维度
        
        返回:
            最优维度
        """
        model_dim = self.pricing['dimensions']
        
        if target_dimensions > model_dim:
            return model_dim
        
        # 必须是8的倍数
        optimal = (target_dimensions // 8) * 8
        
        return max(8, optimal)
