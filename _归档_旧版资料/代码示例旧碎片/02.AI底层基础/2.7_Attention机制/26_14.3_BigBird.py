class BigBirdAttention(nn.Module):
    """BigBird 注意力
    
    结合三种模式:
    1. Random attention: 随机连接捕获全局信息
    2. Window attention: 局部窗口捕获近邻信息  
    3. Global attention: 全局token聚合信息
    """
    
    def __init__(self, d_model, num_heads, 
                 window_size=3, num_global=1, num_random=3):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.window_size = window_size
        self.num_global = num_global
        self.num_random = num_random
        
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
        
        # 全局token位置（前num_global个）
        global_indices = list(range(self.num_global))
        
        # 初始化输出
        output = torch.zeros_like(Q)
        
        # 预计算全局注意力（所有位置都可以关注全局token）
        global_K = K[:, :, global_indices, :]
        global_V = V[:, :, global_indices, :]
        
        # 计算每个位置的注意力
        for i in range(seq_len):
            q_i = Q[:, :, i:i+1, :]
            
            attention_indices = set()
            
            # 1. 全局位置
            attention_indices.update(global_indices)
            
            # 2. 窗口位置
            half_win = self.window_size // 2
            for j in range(max(0, i - half_win), min(seq_len, i + half_win + 1)):
                attention_indices.add(j)
            
            # 3. 随机位置
            random_indices = torch.randperm(seq_len)[:self.num_random].tolist()
            attention_indices.update(random_indices)
            
            # 计算注意力
            attention_indices = sorted(list(attention_indices))
            
            k_selected = K[:, :, attention_indices, :]
            v_selected = V[:, :, attention_indices, :]
            
            scale = math.sqrt(self.head_dim)
            scores = torch.matmul(q_i, k_selected.transpose(-2, -1)) / scale
            attn = F.softmax(scores, dim=-1)
            
            output[:, :, i:i+1, :] = torch.matmul(attn, v_selected)
        
        # 合并
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, None
