import torch                        # PyTorch核心库
import torch.nn.functional as F     # 神经网络函数

def scaled_dot_product_attention(Q, K, V, mask=None):
    """缩放点积注意力（Scaled Dot-Product Attention）
    
    这是Attention机制的核心计算，公式: Attention(Q,K,V) = softmax(QK^T/sqrt(d_k))V
    
    参数:
        Q: 查询矩阵 (batch_size, num_heads, seq_len_q, d_k)
        K: 键矩阵 (batch_size, num_heads, seq_len_k, d_k)
        V: 值矩阵 (batch_size, num_heads, seq_len_v, d_v)
        mask: 掩码矩阵（可选），用于屏蔽某些位置
    返回:
        output: 注意力输出
        attention_weights: 注意力权重矩阵
    """
    # 获取Q的最后一个维度（每个头的维度）
    d_k = Q.size(-1)
    
    # 计算注意力分数: Q * K^T / sqrt(d_k)
    # matmul: 矩阵乘法
    # transpose(-2, -1): 将K的最后两维转置，即对(d_k, seq_len)转置为(seq_len, d_k)
    # sqrt(d_k): 缩放因子，防止点积结果过大导致softmax梯度消失
    scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(d_k, dtype=torch.float32))
    
    # 应用掩码（如果提供）
    if mask is not None:
        # masked_fill: mask为0的位置填充为-1e9（极大负数）
        # softmax后这些位置趋近于0，实现屏蔽效果
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # 对分数应用softmax，得到注意力权重（每行之和为1）
    # dim=-1: 对最后一个维度（seq_len_k）做softmax
    attention_weights = F.softmax(scores, dim=-1)
    
    # 注意力加权求和: 权重矩阵 * V
    # 结果形状: (batch_size, num_heads, seq_len_q, d_v)
    output = torch.matmul(attention_weights, V)
    
    return output, attention_weights

if __name__ == "__main__":
    # 测试自注意力机制
    batch_size = 32                   # 批大小
    num_heads = 8                     # 注意力头数
    seq_len = 10                      # 序列长度
    d_k = 64                          # 每个头的维度
    
    # 创建随机Q, K, V矩阵
    # 形状: (batch_size, num_heads, seq_len, d_k)
    Q = torch.randn(batch_size, num_heads, seq_len, d_k)
    K = torch.randn(batch_size, num_heads, seq_len, d_k)
    V = torch.randn(batch_size, num_heads, seq_len, d_k)
    
    # 计算自注意力
    out, attn_weights = scaled_dot_product_attention(Q, K, V)
    
    print("自注意力输出形状:", out.shape)
    # 输出: torch.Size([32, 8, 10, 64])
    
    print("注意力权重形状:", attn_weights.shape)
    # 输出: torch.Size([32, 8, 10, 10])
    # 每个查询位置与所有键位置的注意力权重
