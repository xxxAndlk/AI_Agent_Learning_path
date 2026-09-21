# 注意力权重可视化
def visualize_attention(attention_weights, tokens):
    """
    attention_weights: (seq_len, seq_len)
    tokens: 词元列表
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(attention_weights, 
                xticklabels=tokens,
                yticklabels=tokens,
                cmap='viridis')
    plt.title("Attention Weights")
    plt.show()
