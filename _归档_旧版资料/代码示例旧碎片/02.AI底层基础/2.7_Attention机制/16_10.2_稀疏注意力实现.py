class SparseAttention(nn.Module):
    """通用稀疏注意力模块
    
    支持多种稀疏模式的组合。
    """
    
    def __init__(self, d_model, num_heads, window_size=128, 
                 global_tokens=4, sparse_type='fixed'):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.window_size = window_size
        self.global_tokens = global_tokens
        self.sparse_type = sparse_type
        
        # 标准投影
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def _create_sparse_mask(self, seq_len, device):
        """创建稀疏注意力掩码"""
        mask = torch.zeros(seq_len, seq_len, device=device)
        
        if self.sparse_type == 'fixed':
            # Fixed: 每隔固定距离设置关注点
            step = seq_len // self.global_tokens
            for i in range(self.global_tokens):
                pos = i * step
                mask[pos, :] = 1  # 全局位置关注所有
            mask[:, :self.global_tokens] = 1  # 所有位置关注全局
            
        elif self.sparse_type == 'strided':
            # Strided: 固定步长跳跃
            stride = 8
            for i in range(0, seq_len, stride):
                mask[i, :] = 1
                
        elif self.sparse_type == 'block':
            # Block Sparse: 分块对角矩阵
            block_size = self.window_size
            for i in range(0, seq_len, block_size):
                end = min(i + block_size, seq_len)
                mask[i:end, i:end] = 1
                
        elif self.sparse_type == 'global_local':
            # Global + Local: 全局token + 局部窗口
            # 全局token
            mask[:self.global_tokens, :] = 1
            mask[:, :self.global_tokens] = 1
            
            # 局部窗口
            half_window = self.window_size // 2
            for i in range(self.global_tokens, seq_len):
                start = max(self.global_tokens, i - half_window)
                end = min(seq_len, i + half_window)
                mask[i, start:end] = 1
        
        return mask.bool()
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        # 投影
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        # 转换维度 (batch, heads, seq, dim)
        Q = Q.transpose(1, 2)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)
        
        # 创建或使用传入的稀疏掩码
        if mask is None:
            sparse_mask = self._create_sparse_mask(seq_len, x.device)
            # 扩展到多头维度
            sparse_mask = sparse_mask.unsqueeze(0).unsqueeze(0)  # (1, 1, seq, seq)
        else:
            sparse_mask = mask
        
        # 计算注意力分数
        scale = math.sqrt(self.head_dim)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / scale
        
        # 应用稀疏掩码
        scores = scores.masked_fill(~sparse_mask, float('-inf'))
        
        # Softmax和加权求和
        attention = F.softmax(scores, dim=-1)
        output = torch.matmul(attention, V)
        
        # 合并多头
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, attention


class BlockSparseAttention(nn.Module):
    """Block Sparse Attention - 更高效的稀疏实现
    
    使用分块计算避免创建完整掩码矩阵。
    """
    
    def __init__(self, d_model, num_heads, block_size=64, num_local_blocks=2):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.block_size = block_size
        self.num_local_blocks = num_local_blocks
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        
        # 计算块数
        num_blocks = (seq_len + self.block_size - 1) // self.block_size
        
        # 投影并 reshape 为块形式
        Q = self.W_q(x).view(batch_size, num_blocks, self.block_size, 
                            self.num_heads, self.head_dim)
        K = self.W_k(x).view(batch_size, num_blocks, self.block_size,
                            self.num_heads, self.head_dim)
        V = self.W_v(x).view(batch_size, num_blocks, self.block_size,
                            self.num_heads, self.head_dim)
        
        # 计算块级注意力 (简化版)
        # 实际实现需要更复杂的块间连接模式
        output = []
        attention_weights = []
        
        for i in range(num_blocks):
            # 当前块
            q_block = Q[:, i]  # (batch, block, heads, dim)
            
            # 相关块（局部窗口 + 可能的全局块）
            start = max(0, i - self.num_local_blocks)
            end = min(num_blocks, i + self.num_local_blocks + 1)
            
            k_block = K[:, start:end].view(
                batch_size, (end - start) * self.block_size,
                self.num_heads, self.head_dim
            )
            v_block = V[:, start:end].view(
                batch_size, (end - start) * self.block_size,
                self.num_heads, self.head_dim
            )
            
            # 计算块内注意力
            scores = torch.matmul(q_block, k_block.transpose(-2, -1))
            scores = scores / math.sqrt(self.head_dim)
            
            attn = F.softmax(scores, dim=-1)
            out = torch.matmul(attn, v_block)
            
            output.append(out)
            attention_weights.append(attn)
        
        # 合并块
        output = torch.cat(output, dim=1).reshape(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        attention_weights = torch.cat(attention_weights, dim=1)
        
        return output, attention_weights
