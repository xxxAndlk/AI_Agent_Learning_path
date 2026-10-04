import torch
import torch.nn as nn
import math

class RoPE(nn.Module):
    """旋转位置编码 (RoPE)
    
    核心公式:
        RoPE(x, pos) = W · [cos(pos·θ)·x_even - sin(pos·θ)·x_odd,
                           sin(pos·θ)·x_even + cos(pos·θ)·x_odd]
    """
    def __init__(self, dim, base=10000):
        super().__init__()
        self.dim = dim  # 嵌入维度
        self.base = base  # 基础频率
        
        # 预计算旋转角度: θ_i = base^(-2i/dim)
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer('inv_freq', inv_freq)
    
    def forward(self, x, seq_len=None):
        """
        参数:
            x: 输入张量 (batch, seq_len, dim)
            seq_len: 序列长度
        返回:
            带有位置编码的张量
        """
        if seq_len is None:
            seq_len = x.size(1)
        
        # 生成位置编码: (seq_len, dim)
        t = torch.arange(seq_len, device=x.device, dtype=self.inv_freq.dtype)
        emb = torch.einsum('i,j->ij', t, self.inv_freq)  # (seq_len, dim/2)
        
        # 拼接sin和cos: (seq_len, dim)
        emb = torch.cat([emb, emb], dim=-1)
        
        # 计算cos和sin
        cos = emb.cos()
        sin = emb.sin()
        
        # 应用旋转: RoPE(x) = x * cos + rotate(x) * sin
        # 其中 rotate(x) = [-x[..., 1::2], x[..., ::2]]
        x1 = x[..., ::2]  # 偶数索引
        x2 = x[..., 1::2]  # 奇数索引
        
        # 旋转后的表示
        rotated = torch.cat([-x2, x1], dim=-1)
        
        # 应用旋转公式
        return x * cos.unsqueeze(0) + rotated * sin.unsqueeze(0)


class RoPEAttention(nn.Module):
    """集成RoPE的多头自注意力"""
    
    def __init__(self, embed_size, heads, base=10000):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        
        self.Wq = nn.Linear(embed_size, embed_size)
        self.Wk = nn.Linear(embed_size, embed_size)
        self.Wv = nn.Linear(embed_size, embed_size)
        self.Wo = nn.Linear(embed_size, embed_size)
        
        # RoPE模块
        self.rope = RoPE(self.head_dim, base)
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        # 线性投影
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim)
        K = self.Wk(x).view(batch_size, seq_len, self.heads, self.head_dim)
        V = self.Wv(x).view(batch_size, seq_len, self.heads, self.head_dim)
        
        # 对Q和K应用RoPE（只对位置维度应用）
        # 形状: (batch, heads, seq_len, head_dim)
        Q = Q.transpose(1, 2)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)
        
        # 应用旋转位置编码到每个头
        for h in range(self.heads):
            Q[:, h] = self.rope(Q[:, h], seq_len)
            K[:, h] = self.rope(K[:, h], seq_len)
        
        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-1e9'))
        
        attn_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        
        # 合并多头
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        
        return self.Wo(output), attn_weights
