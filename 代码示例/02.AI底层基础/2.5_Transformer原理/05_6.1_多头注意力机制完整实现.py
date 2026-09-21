import torch                        # PyTorch核心库
import torch.nn as nn               # 神经网络模块
import torch.nn.functional as F     # 神经网络函数（包含softmax等）

class MultiHeadAttention(nn.Module):
    """多头注意力机制（Multi-Head Self-Attention）
    
    将查询、键、值投影到多个子空间，并行计算注意力，然后拼接
    
    核心公式:
        MultiHead(Q,K,V) = Concat(head_1,...,head_h)W^O
        where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
    """
    def __init__(self, embed_size, heads):
        """
        参数:
            embed_size: 词嵌入维度（如BERT-base为768）
            heads: 注意力头数（如8或12）
        """
        super().__init__()
        self.embed_size = embed_size  # 嵌入维度
        self.heads = heads            # 注意力头数
        self.head_dim = embed_size // heads  # 每个头的维度
        
        # 确保embed_size能被heads整除
        assert self.head_dim * heads == embed_size, "Embedding维度必须能被头数整除"
        
        # 定义线性变换层（投影矩阵）：将输入投影到Q、K、V空间
        # 这些是可学习的参数矩阵
        self.Wq = nn.Linear(embed_size, embed_size)  # 查询投影 W_Q
        self.Wk = nn.Linear(embed_size, embed_size)  # 键投影 W_K
        self.Wv = nn.Linear(embed_size, embed_size)  # 值投影 W_V
        self.Wo = nn.Linear(embed_size, embed_size)  # 输出投影 W_O（拼接后）
    
    def forward(self, q, k, v, mask=None):
        """前向传播
        
        参数:
            q: 查询张量 (batch_size, seq_len, embed_size)
            k: 键张量 (batch_size, seq_len, embed_size)
            v: 值张量 (batch_size, seq_len, embed_size)
            mask: 掩码张量（可选，用于屏蔽某些位置）
        返回:
            output: 注意力输出
            attention_weights: 注意力权重（用于可视化）
        """
        batch_size = q.shape[0]         # 获取batch大小
        
        # 步骤1：线性投影 Q, K, V
        # 公式: Q = X·W_Q, K = X·W_K, V = X·W_V
        # 形状: (batch_size, seq_len, embed_size)
        Q = self.Wq(q)
        K = self.Wk(k)
        V = self.Wv(v)
        
        # 步骤2：将Q, K, V分割成多个头
        # view: 改变形状为 (batch_size, seq_len, heads, head_dim)
        # transpose: 变为 (batch_size, heads, seq_len, head_dim) 以便并行计算
        # 这一步是关键：将embed_size维度拆分为heads×head_dim
        Q = Q.view(batch_size, -1, self.heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, -1, self.heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, -1, self.heads, self.head_dim).transpose(1, 2)
        
        # 步骤3：计算注意力分数: scores = Q * K^T / sqrt(d_k)
        # transpose(-2, -1): 将最后两维转置，即对(head_dim, seq_len)转置为(seq_len, head_dim)
        # 结果形状: (batch_size, heads, seq_len, seq_len)
        # 这个矩阵表示每个位置对其他所有位置的注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(self.head_dim, dtype=torch.float32))
        
        # 步骤4：应用掩码（如果提供）
        if mask is not None:
            # masked_fill: 将mask为0的位置填充为极小的负数，softmax后变为0
            # 这样被mask的位置不会影响注意力计算
            scores = scores.masked_fill(mask == 0, float("-1e20"))
        
        # 步骤5：计算注意力权重（对最后一个维度做softmax）
        # 将分数转换为概率分布，每行和为1
        # 形状保持: (batch_size, heads, seq_len, seq_len)
        attention_weights = F.softmax(scores, dim=-1)
        
        # 步骤6：注意力加权求和: output = attention_weights * V
        # 每个位置的输出是所有位置的加权平均
        # 形状: (batch_size, heads, seq_len, head_dim)
        output = torch.matmul(attention_weights, V)
        
        # 步骤7：拼接多个头的结果
        # transpose: 变回 (batch_size, seq_len, heads, head_dim)
        # contiguous: 确保张量在内存中连续（view操作需要）
        # view: 合并最后两维为embed_size
        # 这一步将多头输出重新组合成一个整体
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.embed_size)
        
        # 步骤8：最终线性投影
        # 通过W_O将拼接后的向量投影到输出空间
        output = self.Wo(output)
        
        return output, attention_weights
