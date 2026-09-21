# RFA (Rectified Feature Attention) 核心实现
class RFA(nn.Module):
    """Random Feature Attention - Google Research 2021
    
    使用随机傅里叶特征近似RBF核，实现高质量线性注意力。
    """
    
    def __init__(self, d_model, num_heads, rff_dim=64):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.rff_dim = rff_dim  # 随机特征维度
        
        # 投影
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        # 随机特征映射参数
        self.W_RFF = nn.Parameter(
            torch.randn(self.head_dim, rff_dim * 2) * 0.02
        )
    
    def _rff_mapping(self, x):
        """随机傅里叶特征映射
        
        φ(x) = [cos(xW + b), sin(xW + b)]
        """
        # 采样随机偏置
        b = torch.randn(x.shape[0], x.shape[1], self.rff_dim * 2, device=x.device)
        
        # 线性变换
        x_proj = torch.matmul(x, self.W_RFF)
        
        # 添加偏置并应用三角函数
        x_proj = x_proj + b
        phi = torch.cat([torch.cos(x_proj), torch.sin(x_proj)], dim=-1)
        
        return phi
    
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        # RFF映射
        Q_rff = self._rff_mapping(Q)
        K_rff = self._rff_mapping(K)
        
        # 线性注意力计算
        # KV = Σⱼ φ(kⱼ) ⊗ vⱼ
        KV = torch.einsum('bnhd,bnhf->bdhf', K_rff, V)
        
        # Z = Σⱼ φ(kⱼ)
        Z = K_rff.sum(dim=1)  # (batch, heads, rff_dim*2)
        
        # 输出计算
        output = torch.einsum('bnrd,bdhf->bnhf', Q_rff, KV)
        
        # 归一化
        denom = torch.einsum('bnrd,bd->bnr', Q_rff, Z).unsqueeze(-1)
        output = output / (denom + 1e-8)
        
        # 合并并输出
        output = output.reshape(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, None
