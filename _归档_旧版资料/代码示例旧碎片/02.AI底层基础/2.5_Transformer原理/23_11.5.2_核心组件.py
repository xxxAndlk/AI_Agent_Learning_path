class LLaMAConfig:
    """LLaMA配置"""
    vocab_size = 32000
    hidden_size = 4096
    intermediate_size = 11008  # 约2.7倍hidden_size
    num_hidden_layers = 32
    num_attention_heads = 32
    num_key_value_heads = 8  # GQA
    max_position_embeddings = 2048

class LLaMAAttention(nn.Module):
    """LLaMA使用的注意力"""
    
    def __init__(self, config: LLaMAConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.num_kv_heads = config.num_key_value_heads
        self.head_dim = config.hidden_size // config.num_attention_heads
        
        # 投影层
        self.q_proj = nn.Linear(config.hidden_size, config.hidden_size)
        self.k_proj = nn.Linear(config.hidden_size, config.num_key_value_heads * self.head_dim)
        self.v_proj = nn.Linear(config.hidden_size, config.num_key_value_heads * self.head_dim)
        self.o_proj = nn.Linear(config.hidden_size, config.hidden_size)
        
        # RoPE
        self.rope = RoPE(self.head_dim, base=10000)
    
    def forward(self, x, attention_mask=None):
        # 投影并分头
        B, T, _ = x.size()
        
        q = self.q_proj(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.num_kv_heads, self.head_dim).transpose(1, 2)
        
        # 应用RoPE
        q = self.rope(q, T)
        k = self.rope(k, T)
        
        # GQA: 扩展K, V
        if self.num_kv_heads < self.num_heads:
            k = k.repeat_interleave(self.num_heads // self.num_kv_heads, dim=1)
            v = v.repeat_interleave(self.num_heads // self.num_kv_heads, dim=1)
        
        # 注意力计算
        out = F.scaled_dot_product_attention(q, k, v, attn_mask=attention_mask)
        
        return self.o_proj(out.transpose(1, 2).contiguous().view(B, T, self.hidden_size))
