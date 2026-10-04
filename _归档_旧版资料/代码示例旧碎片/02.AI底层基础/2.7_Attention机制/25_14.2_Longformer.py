class LongformerAttention(nn.Module):
    """Longformer 注意力
    
    特点:
    1. 滑动窗口注意力 (局部交互)
    2. 全局注意力 (特定位置可关注所有位置)
    3. 膨胀滑动窗口 (扩大感受野)
    """
    
    def __init__(self, d_model, num_heads, window_size=512, 
                 global_indices=None, dilation=1):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.window_size = window_size
        self.dilation = dilation
        self.global_indices = global_indices or [0]  # 默认第一个token是全局的
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        
        # 投影
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        scale = math.sqrt(self.head_dim)
        
        # 初始化输出
        output = torch.zeros_like(Q)
        
        # 识别全局和局部位置
        is_global = torch.zeros(seq_len, dtype=torch.bool, device=x.device)
        is_local = ~is_global
        
        for idx in self.global_indices:
            is_global[idx] = True
        
        # 为每个位置计算注意力
        for i in range(seq_len):
            if is_global[i]:
                # 全局位置：关注所有位置
                q_i = Q[:, :, i:i+1, :]  # (batch, heads, 1, dim)
                scores = torch.matmul(q_i, K.transpose(-2, -1)) / scale
                attn = F.softmax(scores, dim=-1)
                output[:, :, i:i+1, :] = torch.matmul(attn, V)
            else:
                # 局部位置：只关注窗口内
                start = max(0, i - self.window_size // 2)
                end = min(seq_len, i + self.window_size // 2 + 1)
                
                # 膨胀窗口
                if self.dilation > 1:
                    start_indices = torch.arange(start, end, self.dilation, device=x.device)
                    start = start_indices[0].item()
                    end = min(start_indices[-1].item() + 1, seq_len)
                
                q_i = Q[:, :, i:i+1, :]
                k_window = K[:, :, start:end, :]
                v_window = V[:, :, start:end, :]
                
                scores = torch.matmul(q_i, k_window.transpose(-2, -1)) / scale
                attn = F.softmax(scores, dim=-1)
                output[:, :, i:i+1, :] = torch.matmul(attn, v_window)
        
        # 合并输出
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, None
