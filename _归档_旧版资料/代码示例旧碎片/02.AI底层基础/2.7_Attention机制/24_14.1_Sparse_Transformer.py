class SparseTransformerLayer(nn.Module):
    """Sparse Transformer层
    
    结合了:
    1. 稀疏注意力 (Strided + Fixed)
    2. 残差连接
    3. 层归一化
    """
    
    def __init__(self, d_model, num_heads, sparse_type='fixed_strided'):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.sparse_type = sparse_type
        
        # 注意力
        self.self_attn = SparseTransformerAttention(d_model, num_heads, sparse_type)
        
        # FFN
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Linear(d_model * 4, d_model)
        )
        
        # 层归一化
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
    
    def forward(self, x, mask=None):
        # 自注意力 + 残差
        attn_out, attn_weights = self.self_attn(x, mask)
        x = self.norm1(x + attn_out)
        
        # FFN + 残差
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        
        return x, attn_weights


class SparseTransformerAttention(nn.Module):
    """Sparse Transformer注意力
    
    使用固定的稀疏模式：
    - Strided: 捕获局部结构
    - Fixed: 捕获全局信息
    """
    
    def __init__(self, d_model, num_heads, sparse_type='fixed_strided'):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.sparse_type = sparse_type
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        # 投影
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # 创建稀疏掩码
        sparse_mask = self._create_sparse_mask(seq_len, x.device, x.dtype)
        
        # 计算注意力
        scale = math.sqrt(self.head_dim)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / scale
        
        if sparse_mask is not None:
            scores = scores.masked_fill(sparse_mask == 0, float('-inf'))
        
        attn = F.softmax(scores, dim=-1)
        output = torch.matmul(attn, V)
        
        # 输出
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, attn
    
    def _create_sparse_mask(self, seq_len, device, dtype):
        """创建Sparse Transformer的稀疏掩码
        
        结合 Strided 和 Fixed 两种模式。
        """
        mask = torch.zeros(seq_len, seq_len, device=device, dtype=dtype)
        
        # Strided 注意力 (注意力跳跃位置)
        stride = int(math.sqrt(seq_len))
        for i in range(seq_len):
            for j in range(0, seq_len, stride):
                if j <= i:
                    mask[i, j] = 1
        
        # Fixed 注意力 (固定间隔的全局位置)
        fixed_interval = stride
        for i in range(seq_len):
            for j in range(0, seq_len, fixed_interval):
                mask[i, j] = 1
        
        # 加上对角线（自身）
        mask = mask + torch.eye(seq_len, device=device, dtype=dtype)
        
        return mask.bool()
