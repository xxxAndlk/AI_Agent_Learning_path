class SlidingWindowAttention(nn.Module):
    """滑动窗口注意力 - 高效处理长序列
    
    每个token只关注固定窗口内的其他token。
    """
    
    def __init__(self, d_model, num_heads, window_size=512):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.window_size = window_size
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        Q = Q.transpose(1, 2)  # (batch, heads, seq, dim)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)
        
        # 计算相对位置编码的缩放因子
        scale = math.sqrt(self.head_dim)
        
        # 创建滑动窗口掩码
        # 使用上三角和下三角创建因果窗口
        if mask is None:
            # 创建滑动窗口掩码
            mask = torch.full((seq_len, seq_len), float('-inf'), device=x.device)
            half_window = self.window_size // 2
            
            for i in range(seq_len):
                start = max(0, i - half_window)
                end = min(seq_len, i + half_window + 1)
                mask[i, start:end] = 0
            
            mask = mask.unsqueeze(0).unsqueeze(0)  # (1, 1, seq, seq)
        
        # 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / scale
        scores = scores + mask
        
        attention = F.softmax(scores, dim=-1)
        attention = F.dropout(attention, p=0.1, training=self.training)
        
        output = torch.matmul(attention, V)
        
        # 合并多头
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, attention


class EfficientSlidingWindowAttention(nn.Module):
    """高效滑动窗口注意力 - 使用分块计算
    
    避免创建完整的 n×n 注意力矩阵。
    """
    
    def __init__(self, d_model, num_heads, window_size=512):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.window_size = window_size
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        Q = Q.transpose(1, 2)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)
        
        scale = math.sqrt(self.head_dim)
        half_window = self.window_size // 2
        
        output = torch.zeros_like(Q)
        
        # 分块计算注意力
        block_size = 128  # 每次处理128个query
        
        for i in range(0, seq_len, block_size):
            end_i = min(i + block_size, seq_len)
            
            # 当前块的query
            q_block = Q[:, :, i:end_i, :]  # (batch, heads, block, dim)
            
            # 相关key-value范围
            start_k = max(0, i - half_window)
            end_k = min(seq_len, end_i + half_window)
            
            k_block = K[:, :, start_k:end_k, :]
            v_block = V[:, :, start_k:end_k, :]
            
            # 计算局部注意力
            scores = torch.matmul(q_block, k_block.transpose(-2, -1)) / scale
            
            # 局部掩码（可选因果掩码）
            attn = F.softmax(scores, dim=-1)
            out_block = torch.matmul(attn, v_block)
            
            output[:, :, i:end_i, :] = out_block
        
        # 合并
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, None
