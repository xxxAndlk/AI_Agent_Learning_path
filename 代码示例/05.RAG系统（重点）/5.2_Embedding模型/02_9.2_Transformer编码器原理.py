import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    """自注意力机制"""
    
    def __init__(self, embed_size: int, heads: int):
        """
        初始化自注意力
        
        参数:
            embed_size: 嵌入维度
            heads: 注意力头数
        """
        super(SelfAttention, self).__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        
        assert (
            self.head_dim * heads == embed_size
        ), "embed_size must be divisible by heads"
        
        # 线性变换
        self.values = nn.Linear(embed_size, embed_size)
        self.keys = nn.Linear(embed_size, embed_size)
        self.queries = nn.Linear(embed_size, embed_size)
        self.fc_out = nn.Linear(embed_size, embed_size)
    
    def forward(self, values, keys, query, mask=None):
        """
        前向传播
        
        参数:
            values: 值向量
            keys: 键向量
            query: 查询向量
            mask: 掩码
        
        返回:
            注意力输出
        """
        N = query.shape[0]
        value_len, key_len, query_len = values.shape[1], keys.shape[1], query.shape[1]
        
        # 分割成多个头
        values = values.reshape(N, value_len, self.heads, self.head_dim)
        keys = keys.reshape(N, key_len, self.heads, self.head_dim)
        queries = query.reshape(N, query_len, self.heads, self.head_dim)
        
        # 计算注意力分数
        energy = torch.einsum("nqhd,nkhd->nhqk", [queries, keys])
        
        if mask is not None:
            energy = energy.masked_fill(mask == 0, float("-1e20"))
        
        attention = torch.softmax(energy / (self.embed_size ** (1/2)), dim=3)
        
        # 应用注意力
        out = torch.einsum("nhql,nlhd->nqhd", [attention, values]).reshape(
            N, query_len, self.heads * self.head_dim
        )
        
        return self.fc_out(out)


class TransformerBlock(nn.Module):
    """Transformer块"""
    
    def __init__(self, embed_size: int, heads: int, dropout: float, forward_expansion: int):
        """
        初始化Transformer块
        
        参数:
            embed_size: 嵌入维度
            heads: 注意力头数
            dropout: Dropout比率
            forward_expansion: 前馈网络扩展倍数
        """
        super(TransformerBlock, self).__init__()
        
        self.attention = SelfAttention(embed_size, heads)
        self.norm1 = nn.LayerNorm(embed_size)
        self.norm2 = nn.LayerNorm(embed_size)
        
        self.feed_forward = nn.Sequential(
            nn.Linear(embed_size, forward_expansion * embed_size),
            nn.ReLU(),
            nn.Linear(forward_expansion * embed_size, embed_size)
        )
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, value, key, query, mask=None):
        """
        前向传播
        """
        attention = self.attention(value, key, query, mask)
        
        x = self.dropout(self.norm1(attention + query))
        
        forward = self.feed_forward(x)
        
        out = self.dropout(self.norm2(forward + x))
        
        return out
