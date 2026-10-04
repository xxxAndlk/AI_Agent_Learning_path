import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def visualize_attention_heatmap(attention_weights, tokens, save_path=None):
    """绘制注意力权重热力图
    
    Args:
        attention_weights: (num_heads, seq_len, seq_len) 或 (seq_len, seq_len)
        tokens: token列表
        save_path: 保存路径（可选）
    """
    # 处理不同形状
    if len(attention_weights.shape) == 3:
        # 取第一个头的注意力
        attn = attention_weights[0]
    else:
        attn = attention_weights
    
    # 转换为numpy
    if hasattr(attn, 'cpu'):
        attn = attn.cpu().detach().numpy()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 绘制热力图
    sns.heatmap(attn, 
                xticklabels=tokens,
                yticklabels=tokens,
                cmap='YlOrRd',
                annot=False,
                square=True,
                cbar_kws={'label': 'Attention Weight'},
                ax=ax)
    
    ax.set_xlabel('Key Positions', fontsize=12)
    ax.set_ylabel('Query Positions', fontsize=12)
    ax.set_title('Attention Weights Heatmap', fontsize=14)
    
    # 旋转标签
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"热力图已保存到: {save_path}")
    
    plt.show()


def visualize_multi_head_attention(attention_weights, tokens, num_heads=8):
    """可视化多头的注意力模式
    
    每个头可能关注不同类型的信息（语法、语义、位置等）。
    """
    num_heads = attention_weights.shape[0]
    seq_len = attention_weights.shape[1]
    
    # 计算行列数
    cols = 4
    rows = (num_heads + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
    axes = axes.flatten() if num_heads > 1 else [axes]
    
    for head_idx in range(num_heads):
        ax = axes[head_idx]
        attn = attention_weights[head_idx].cpu().detach().numpy()
        
        sns.heatmap(attn, 
                   xticklabels=[],
                   yticklabels=[],
                   cmap='viridis',
                   ax=ax,
                   cbar=False)
        
        ax.set_title(f'Head {head_idx}', fontsize=10)
    
    # 隐藏多余的子图
    for i in range(num_heads, len(axes)):
        axes[i].axis('off')
    
    plt.suptitle('Multi-Head Attention Patterns', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.show()


def visualize_token_attention(attention_weights, tokens, token_idx, top_k=5):
    """可视化特定token对其他token的注意力分布
    
    Args:
        attention_weights: (num_heads, seq_len, seq_len)
        tokens: token列表
        token_idx: 目标token索引
        top_k: 显示前k个高注意力位置
    """
    # 平均所有头
    avg_attn = attention_weights.mean(dim=0)  # (seq_len, seq_len)
    
    # 获取目标token的注意力分布
    attn_distribution = avg_attn[token_idx].cpu().detach().numpy()
    
    # 找出top-k
    top_indices = np.argsort(attn_distribution)[::-1][:top_k]
    top_values = attn_distribution[top_indices]
    
    # 绘制条形图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#e74c3c' if i == token_idx else '#3498db' for i in top_indices]
    
    bars = ax.barh(range(top_k), top_values[::-1], color=colors[::-1])
    
    # 设置标签
    top_tokens = [tokens[i] for i in top_indices]
    ax.set_yticks(range(top_k))
    ax.set_yticklabels([f'{tokens[token_idx]} → {t}' for t in top_tokens[::-1]])
    
    ax.set_xlabel('Attention Weight')
    ax.set_title(f'注意力分布: token "{tokens[token_idx]}" (idx={token_idx})')
    
    # 添加数值标签
    for bar, val in zip(bars, top_values[::-1]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
               f'{val:.3f}', va='center')
    
    plt.tight_layout()
    plt.show()
