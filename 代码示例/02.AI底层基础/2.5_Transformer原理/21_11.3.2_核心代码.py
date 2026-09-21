class GPTConfig:
    """GPT配置参数"""
    vocab_size = 50257
    max_position_embeddings = 1024
    n_layer = 12
    n_head = 12
    n_embd = 768

class GPTBlock(nn.Module):
    """GPTTransformer块（带因果掩码）"""
    
    def __init__(self, config: GPTConfig):
        super().__init__()
        self.attention = CausalSelfAttention(config)
        self.ln_1 = nn.LayerNorm(config.n_embd)
        self.ln_2 = nn.LayerNorm(config.n_embd)
        
        self.mlp = nn.Sequential(
            nn.Linear(config.n_embd, 4 * config.n_embd),
            nn.GELU(),
            nn.Linear(4 * config.n_embd, config.n_embd)
        )
    
    def forward(self, x):
        # 因果自注意力
        x = x + self.attention(self.ln_1(x))
        # 前馈网络
        x = x + self.mlp(self.ln_2(x))
        return x

class CausalSelfAttention(nn.Module):
    """GPT的因果自注意力"""
    
    def __init__(self, config: GPTConfig):
        super().__init__()
        self.n_head = config.n_head
        self.n_embd = config.n_embd
        self.head_dim = config.n_embd // config.n_head
        
        # Q, K, V, 输出投影
        self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd)
        self.c_proj = nn.Linear(config.n_embd, config.n_embd)
        
        # 注册因果掩码
        self.register_buffer(
            "bias",
            torch.tril(torch.ones(config.max_position_embeddings, 
                                 config.max_position_embeddings))
            .view(1, 1, config.max_position_embeddings, config.max_position_embeddings)
        )
    
    def forward(self, x):
        B, T, C = x.size()
        
        # 投影Q, K, V
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)
        
        # 分多头
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        
        # 注意力计算
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
        
        # 应用因果掩码
        att = att.masked_fill(self.bias[:, :, :T, :T] == 0, float('-inf'))
        
        att = F.softmax(att, dim=-1)
        y = att @ v
        
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.c_proj(y)
