class AttentionVisualizer:
    """综合注意力可视化工具"""
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
    
    def extract_attention(self, text, layer_idx=-1, head_idx=None):
        """从模型中提取注意力权重
        
        Args:
            text: 输入文本
            layer_idx: 要提取的层索引 (-1表示最后一层)
            head_idx: 要提取的头索引 (None表示所有头)
        
        Returns:
            attention_weights: 注意力权重
            tokens: token列表
        """
        # Tokenize
        inputs = self.tokenizer(text, return_tensors='pt')
        
        # 获取输出
        with torch.no_grad():
            outputs = self.model(**inputs, output_attentions=True)
        
        attentions = outputs.attentions
        
        # 获取指定层
        layer_attn = attentions[layer_idx]  # (batch, heads, seq, seq)
        
        # 选择头
        if head_idx is not None:
            layer_attn = layer_attn[:, head_idx:head_idx+1, :, :]
        
        # 获取tokens
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        return layer_attn[0], tokens
    
    def comprehensive_analysis(self, text):
        """综合分析文本的注意力模式"""
        attentions, tokens = self.extract_attention(text)
        
        print(f"文本: {text}")
        print(f"Tokens: {tokens}")
        print(f"注意力形状: {attentions.shape}")
        print("="*50)
        
        # 1. 多头注意力可视化
        print("\n1. 多头注意力模式:")
        visualize_multi_head_attention(attentions, tokens)
        
        # 2. 注意力流
        print("\n2. 跨层注意力分析:")
        all_attentions = self.model(
            **self.tokenizer(text, return_tensors='pt'),
            output_attentions=True
        ).attentions
        
        visualize_attention_flow(all_attentions)
        
        # 3. Attention Rollout
        print("\n3. Attention Rollout分析:")
        visualize_attention_rollout(all_attentions, tokens)
        
        # 4. 聚合分析
        print("\n4. 注意力聚合统计:")
        avg_attn = attentions.mean(dim=0)
        
        # 每个token收到的总注意力
        attention_received = avg_attn.sum(dim=0)
        top_attended = attention_received.argsort(descending=True)[:5]
        
        print("接收最多注意力的token:")
        for idx in top_attended:
            print(f"  {tokens[idx]}: {attention_received[idx].item():.4f}")
        
        return attentions, tokens
