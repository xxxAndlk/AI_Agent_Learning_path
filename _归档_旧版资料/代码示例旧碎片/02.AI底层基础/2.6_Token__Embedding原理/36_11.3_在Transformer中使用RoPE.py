class RoPEMultiHeadAttention(nn.Module):
    """使用RoPE的多头注意力机制"""
    
    def __init__(self, dim, num_heads, max_seq_len=512):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        
        # QKV投影
        self.W_q = nn.Linear(dim, dim)
        self.W_k = nn.Linear(dim, dim)
        self.W_v = nn.Linear(dim, dim)
        self.W_o = nn.Linear(dim, dim)
        
        # RoPE
        self.rope = RoPE(self.head_dim, max_seq_len)
        
        self.scale = self.head_dim ** -0.5
    
    def forward(self, x, mask=None):
        """前向传播
        
        参数:
            x: (batch, seq_len, dim)
            mask: 注意力掩码
        """
        batch_size, seq_len, _ = x.shape
        
        # QKV投影
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # 应用RoPE到Q和K（只旋转位置，不改变batch/head维度）
        Q = self.rope(Q.transpose(1, 2)).transpose(1, 2)
        K = self.rope(K.transpose(1, 2)).transpose(1, 2)
        
        # 注意力计算
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))
        
        attn_weights = torch.softmax(attn_scores, dim=-1)
        attn_output = torch.matmul(attn_weights, V)
        
        # 合并多头
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.dim)
        
        return self.W_o(attn_output)

# 使用示例
def use_rope_attention():
    """使用RoPE注意力"""
    
    # 配置
    batch_size = 4
    seq_len = 32
    dim = 256
    num_heads = 8
    
    # 模型
    attention = RoPEMultiHeadAttention(dim, num_heads)
    
    # 输入
    x = torch.randn(batch_size, seq_len, dim)
    
    # 前向传播
    output = attention(x)
    
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {output.shape}")

use_rope_attention()
