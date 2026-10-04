import matplotlib.pyplot as plt

def visualize_attention_flow(attention_weights_list, layer_names=None):
    """可视化跨层的注意力流动（Attention Flow）
    
    展示信息如何在Transformer层之间传递。
    
    Args:
        attention_weights_list: 多层注意力权重列表 [(heads, seq, seq), ...]
        layer_names: 层名称列表
    """

    num_layers = len(attention_weights_list)
    seq_len = attention_weights_list[0].shape[1]
    
    if layer_names is None:
        layer_names = [f'Layer {i+1}' for i in range(num_layers)]
    
    # 平均所有头
    avg_attentions = [attn.mean(dim=0).cpu().detach().numpy() 
                      for attn in attention_weights_list]
    
    # 创建注意力流图
    fig, axes = plt.subplots(1, num_layers, figsize=(4 * num_layers, 4))
    if num_layers == 1:
        axes = [axes]
    
    for idx, (attn, name) in enumerate(zip(avg_attentions, layer_names)):
        ax = axes[idx]
        im = ax.imshow(attn, cmap='Blues', aspect='auto')
        ax.set_title(name)
        ax.set_xlabel('Key')
        ax.set_ylabel('Query')
        
        # 添加颜色条
        if idx == num_layers - 1:
            plt.colorbar(im, ax=ax, fraction=0.046)
    
    plt.suptitle('Attention Flow Across Layers', fontsize=14)
    plt.tight_layout()
    plt.show()


def compute_attention_rollout(attention_weights_list, add_residual=True):
    """计算Attention Rollout
    
    模拟信息在Transformer层之间的流动。
    公式: Rollout_i = Rollout_{i-1} * Attention_i
    
    这可以帮助理解CLS token如何聚合整个序列的信息。
    
    Args:
        attention_weights_list: 多层注意力权重列表
        add_residual: 是否添加残差连接
    
    Returns:
        跨层累积的注意力矩阵
    """
    # 从第一层开始
    num_layers = len(attention_weights_list)
    
    # 取平均头
    attn = attention_weights_list[0].mean(dim=0)  # (seq, seq)
    
    # 添加残差（模拟attention is all you need中的连接）
    if add_residual:
        identity = torch.eye(attn.shape[0], device=attn.device)
        attn = (attn + identity) / 2
    
    rollout = attn
    
    # 逐层累积
    for i in range(1, num_layers):
        layer_attn = attention_weights_list[i].mean(dim=0)
        
        if add_residual:
            identity = torch.eye(layer_attn.shape[0], device=layer_attn.device)
            layer_attn = (layer_attn + identity) / 2
        
        # 矩阵乘法模拟信息传递
        rollout = torch.matmul(rollout, layer_attn)
    
    return rollout


def visualize_attention_rollout(attention_weights_list, tokens, cls_token_idx=0):
    """可视化Attention Rollout结果
    
    展示CLS token如何关注序列中的各个位置。
    """
    # 计算rollout
    rollout = compute_attention_rollout(attention_weights_list)
    
    # 获取CLS token的注意力
    cls_attn = rollout[cls_token_idx].cpu().detach().numpy()
    
    # 绘制
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 热力图
    sns.heatmap(rollout.cpu().detach().numpy(), 
                cmap='Blues',
                xticklabels=tokens[:rollout.shape[0]],
                yticklabels=tokens[:rollout.shape[0]],
                ax=ax1)
    ax1.set_title('Attention Rollout Matrix')
    
    # CLS注意力分布
    ax2.bar(range(len(cls_attn)), cls_attn)
    ax2.set_xlabel('Token Position')
    ax2.set_ylabel('Attention from CLS')
    ax2.set_title(f'CLS Token Attention Distribution')
    
    plt.tight_layout()
    plt.show()
