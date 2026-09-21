def top_k_sampling(logits, k):
    """LLM生成中的Top-K采样"""
    # 获取top-k的值和索引
    top_k_values, top_k_indices = torch.topk(logits, k)
    
    # 创建过滤后的logits
    filtered_logits = torch.full_like(logits, float('-inf'))
    filtered_logits.scatter_(dim=-1, index=top_k_indices, src=top_k_values)
    
    # 计算概率并采样
    probs = F.softmax(filtered_logits, dim=-1)
    return torch.multinomial(probs, 1)
