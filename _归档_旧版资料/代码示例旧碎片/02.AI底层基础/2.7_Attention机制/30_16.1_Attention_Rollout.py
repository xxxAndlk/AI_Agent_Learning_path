import numpy as np

def compute_attention_rollout(attentions, add_residual=True, head_aggregate='mean'):
    """计算Attention Rollout
    
    Args:
        attentions: 多层注意力列表，每项 (batch, heads, seq, seq)
        add_residual: 是否模拟残差连接
        head_aggregate: 'mean' 或 'max'
    
    Returns:
        累积的注意力矩阵 (seq, seq)
    """
    # 聚合多个头
    if head_aggregate == 'mean':
        attn = attentions[0].mean(dim=1)  # (batch, seq, seq)
    elif head_aggregate == 'max':
        attn = attentions[0].max(dim=1)[0]
    
    # 取第一个样本
    attn = attn[0]  # (seq, seq)
    
    # 添加残差（模拟LayerNorm前的残差连接）
    if add_residual:
        num_tokens = attn.shape[0]
        attn = attn + torch.eye(num_tokens, device=attn.device)
        attn = attn / attn.sum(dim=-1, keepdim=True)
    
    rollout = attn
    
    # 逐层累积
    for layer_attn in attentions[1:]:
        if head_aggregate == 'mean':
            layer_attn = layer_attn.mean(dim=1)
        elif head_aggregate == 'max':
            layer_attn = layer_attn.max(dim=1)[0]
        
        layer_attn = layer_attn[0]
        
        if add_residual:
            num_tokens = layer_attn.shape[0]
            layer_attn = layer_attn + torch.eye(num_tokens, device=layer_attn.device)
            layer_attn = layer_attn / layer_attn.sum(dim=-1, keepdim=True)
        
        # 矩阵乘法模拟信息传递
        rollout = torch.matmul(rollout, layer_attn)
    
    return rollout


def analyze_cls_aggregation(rollout, tokens):
    """分析CLS token如何聚合序列信息
    
    Args:
        rollout: Attention Rollout矩阵 (seq, seq)
        tokens: token列表
    
    Returns:
        聚合分析结果
    """
    cls_attention = rollout[0].cpu().numpy()  # CLS对所有位置的注意力
    
    # 排序
    sorted_indices = np.argsort(cls_attention)[::-1]
    
    print("CLS Token 注意力聚合分析:")
    print("=" * 50)
    
    print(f"\n注意力最高的10个位置:")
    for rank, idx in enumerate(sorted_indices[:10]):
        print(f"  {rank+1}. '{tokens[idx]}': {cls_attention[idx]:.4f}")
    
    print(f"\n注意力分布统计:")
    print(f"  最大: {cls_attention.max():.4f}")
    print(f"  最小: {cls_attention.min():.4f}")
    print(f"  均值: {cls_attention.mean():.4f}")
    print(f"  标准差: {cls_attention.std():.4f}")
    
    # 集中度分析
    top_k = [1, 5, 10, 20]
    print(f"\n集中度分析 (前k个位置占比):")
    for k in top_k:
        concentration = cls_attention[sorted_indices[:k]].sum()
        print(f"  Top-{k}: {concentration:.2%}")
    
    return {
        'cls_attention': cls_attention,
        'sorted_indices': sorted_indices
    }
