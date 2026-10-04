class SentenceEmbeddingStrategy:
    """句子嵌入策略"""
    
    @staticmethod
    def cls_pooling(hidden_states, attention_mask=None):
        """
        CLS策略 - 使用[CLS]标记的表示
        
        参数:
            hidden_states: 模型输出的隐藏状态
            attention_mask: 注意力掩码
        
        返回:
            句子嵌入向量
        """
        # 取第一个token（[CLS]）的表示
        return hidden_states[:, 0]
    
    @staticmethod
    def mean_pooling(hidden_states, attention_mask):
        """
        Mean Pooling策略 - 对所有token取平均
        
        参数:
            hidden_states: 模型输出的隐藏状态
            attention_mask: 注意力掩码
        
        返回:
            句子嵌入向量
        """
        # 扩展attention mask以匹配hidden_states的维度
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(
            hidden_states.size()
        ).float()
        
        # 计算加权和
        sum_embeddings = torch.sum(hidden_states * input_mask_expanded, dim=1)
        sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
        
        return sum_embeddings / sum_mask
    
    @staticmethod
    def max_pooling(hidden_states, attention_mask=None):
        """
        Max Pooling策略 - 取每个维度的最大值
        
        参数:
            hidden_states: 模型输出的隐藏状态
            attention_mask: 注意力掩码
        
        返回:
            句子嵌入向量
        """
        # 将padding位置设为很小的值
        if attention_mask is not None:
            mask_expanded = attention_mask.unsqueeze(-1).expand(
                hidden_states.size()
            ).float()
            hidden_states = hidden_states.clone()
            hidden_states[mask_expanded == 0] = -1e9
        
        # 取最大值
        return torch.max(hidden_states, dim=1)[0]
    
    @staticmethod
    def concat_pooling(hidden_states, attention_mask=None):
        """
        Concat策略 - 拼接多种策略的结果
        
        参数:
            hidden_states: 模型输出的隐藏状态
            attention_mask: 注意力掩码
        
        返回:
            句子嵌入向量
        """
        cls_embed = SentenceEmbeddingStrategy.cls_pooling(hidden_states)
        mean_embed = SentenceEmbeddingStrategy.mean_pooling(
            hidden_states, attention_mask
        )
        max_embed = SentenceEmbeddingStrategy.max_pooling(
            hidden_states, attention_mask
        )
        
        # 拼接
        return torch.cat([cls_embed, mean_embed, max_embed], dim=-1)
