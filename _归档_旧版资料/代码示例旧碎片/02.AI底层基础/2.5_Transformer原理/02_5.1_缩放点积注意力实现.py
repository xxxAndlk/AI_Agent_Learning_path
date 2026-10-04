import torch
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None, dropout=None):
    """
    缩放点积注意力
    
    参数:
        Q: 查询矩阵 (batch_size, heads, seq_len, d_k)
        K: 键矩阵   (batch_size, heads, seq_len, d_k)
        V: 值矩阵   (batch_size, heads, seq_len, d_v)
        mask: 掩码 (可选)
        dropout: Dropout层 (可选)
    
    返回:
        output: 注意力输出
        attention_weights: 注意力权重矩阵
    """
    d_k = Q.size(-1)  # 键向量维度
    
    # 步骤1: 计算注意力分数 (Q × K^T)
    # 形状: (batch, heads, seq_len, seq_len)
    scores = torch.matmul(Q, K.transpose(-2, -1))
    
    # 步骤2: 缩放 (÷ √d_k)
    # 原因: 防止点积值过大导致softmax梯度消失
    scores = scores / torch.sqrt(torch.tensor(d_k, dtype=torch.float32))
    
    # 步骤3: 应用掩码（如果有）
    if mask is not None:
        # 将mask为0的位置替换为极小值
        # softmax后这些位置的权重接近0
        scores = scores.masked_fill(mask == 0, float('-1e9'))
    
    # 步骤4: Softmax归一化
    # 在最后一个维度(seq_len)上归一化，每行和为1
    attention_weights = F.softmax(scores, dim=-1)
    
    # 步骤5: Dropout（可选）
    if dropout is not None:
        attention_weights = dropout(attention_weights)
    
    # 步骤6: 加权求和 (Attention × V)
    # 形状: (batch, heads, seq_len, d_v)
    output = torch.matmul(attention_weights, V)
    
    return output, attention_weights
