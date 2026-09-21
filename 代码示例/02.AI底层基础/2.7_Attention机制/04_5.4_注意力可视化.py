def visualize_attention(attention_weights, tokens, head=0):
    """可视化注意力权重
    
    Args:
        attention_weights: (num_heads, seq_len, seq_len)
        tokens: token列表
        head: 要可视化的头索引
    """

    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # 选择一个头
    attn = attention_weights[head].cpu().detach().numpy()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(attn, 
                xticklabels=tokens,
                yticklabels=tokens,
                cmap='viridis',
                annot=True,
                fmt='.2f')
    plt.title(f'Attention Weights - Head {head}')
    plt.xlabel('Key Positions')
    plt.ylabel('Query Positions')
    plt.tight_layout()
    plt.show()
