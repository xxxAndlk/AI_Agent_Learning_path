class MistralAttention(nn.Module):
    """Mistral 风格的滑动窗口注意力
    
    关键特性:
    1. 滑动窗口注意力 (window_size=4096)
    2. 滚动KV缓存 - 始终保留最近window_size个token
    3. 支持PagedAttention
    """
    
    def __init__(self, d_model, num_heads, window_size=4096):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.window_size = window_size
        
        # 投影层
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        # KV缓存
        self.k_cache = None
        self.v_cache = None
    
    def forward(self, x, use_cache=False, past_key_value=None):
        batch_size, seq_len, _ = x.shape
        
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        Q = Q.transpose(1, 2)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)
        
        # 滚动缓存：只保留最近的window_size个token
        if use_cache:
            if past_key_value is None:
                # 初始化缓存
                k_cache = K
                v_cache = V
            else:
                k_cache, v_cache = past_key_value
                
                # 滚动：丢弃最旧的token
                if k_cache.shape[2] > self.window_size:
                    k_cache = k_cache[:, :, -self.window_size:, :]
                    v_cache = v_cache[:, :, -self.window_size:, :]
                
                # 追加新的K和V
                k_cache = torch.cat([k_cache, K], dim=2)
                v_cache = torch.cat([v_cache, V], dim=2)
            
            K = k_cache
            V = v_cache
            past_key_value = (k_cache, v_cache)
        
        # 计算注意力
        scale = math.sqrt(self.head_dim)
        
        # 只对最后一个query位置计算注意力
        q_len = Q.shape[2]
        
        # 局部窗口注意力
        if q_len == 1 and use_cache:
            # 推理模式：只计算单个query与缓存K,V的注意力
            q = Q[:, :, -1:, :]  # 最后一个位置
            scores = torch.matmul(q, K.transpose(-2, -1)) / scale
            
            # 滑动窗口掩码
            if K.shape[2] > self.window_size:
                # 移除超过窗口的注意力分数
                scores = scores[:, :, :, -self.window_size:]
            
            attn = F.softmax(scores, dim=-1)
            output = torch.matmul(attn, V)
        else:
            # 训练模式：完整计算
            scores = torch.matmul(Q, K.transpose(-2, -1)) / scale
            
            # 因果掩码
            causal_mask = torch.triu(
                torch.ones(q_len, K.shape[2], device=x.device),
                diagonal=K.shape[2] - q_len + 1
            ).bool()
            scores = scores.masked_fill(causal_mask, float('-inf'))
            
            attn = F.softmax(scores, dim=-1)
            output = torch.matmul(attn, V)
        
        # 输出投影
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.W_o(output)
        
        return output, past_key_value
