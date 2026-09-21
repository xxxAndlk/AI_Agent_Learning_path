import torch
import torch.nn as nn
import torch.nn.functional as F

class SlidingWindowAttention(nn.Module):
    """滑动窗口注意力 (Sliding Window Attention)
    
    每个位置只关注窗口大小w内的token
    典型配置: w = 512 (Mistral) 或 w = 1024
    """
    
    def __init__(self, embed_size: int, heads: int, window_size: int = 512):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        self.window_size = window_size
        
        self.Wq = nn.Linear(embed_size, embed_size)
        self.Wk = nn.Linear(embed_size, embed_size)
        self.Wv = nn.Linear(embed_size, embed_size)
        self.Wo = nn.Linear(embed_size, embed_size)
    
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None):
        batch_size, seq_len, _ = x.shape
        
        # 投影
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        K = self.Wk(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        V = self.Wv(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        
        # 创建滑动窗口mask
        sliding_mask = self._create_sliding_window_mask(seq_len, Q.device)
        
        # 合并外部mask
        if mask is not None:
            sliding_mask = sliding_mask & mask
        
        # 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        scores = scores.masked_fill(~sliding_mask, float('-1e9'))
        
        attn_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        return self.Wo(output), attn_weights
    
    def _create_sliding_window_mask(self, seq_len: int, device: torch.device):
        """创建滑动窗口mask"""
        # 创建相对位置矩阵
        positions = torch.arange(seq_len, device=device)
        relative_pos = positions.unsqueeze(0) - positions.unsqueeze(1)
        relative_pos = relative_pos.abs()
        
        # 窗口内为True，窗口外为False
        mask = relative_pos <= (self.window_size // 2)
        
        # 添加batch和head维度
        mask = mask.unsqueeze(0).unsqueeze(0)
        
        return mask


class SlidingWindowWithGlobalAttention(nn.Module):
    """滑动窗口 + 全局注意力
    
    大多数token使用滑动窗口，部分token可以关注全部位置（全局token）
    典型应用: Mistral, Quasi-RNN
    """
    
    def __init__(
        self, 
        embed_size: int, 
        heads: int, 
        window_size: int = 512,
        num_global_tokens: int = 2
    ):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        self.window_size = window_size
        self.num_global_tokens = num_global_tokens
        
        self.Wq = nn.Linear(embed_size, embed_size)
        self.Wk = nn.Linear(embed_size, embed_size)
        self.Wv = nn.Linear(embed_size, embed_size)
        self.Wo = nn.Linear(embed_size, embed_size)
    
    def forward(self, x: torch.Tensor):
        """
        假设输入的前num_global_tokens是全局token
        """
        batch_size, seq_len, _ = x.shape
        
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        K = self.Wk(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        V = self.Wv(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        
        # 分离全局token和局部token
        global_q = Q[:, :, :self.num_global_tokens, :]
        local_q = Q[:, :, self.num_global_tokens:, :]
        
        # 创建mask
        mask = self._create_hybrid_mask(seq_len, Q.device)
        
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        scores = scores.masked_fill(~mask, float('-1e9'))
        
        attn_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        return self.Wo(output), attn_weights
    
    def _create_hybrid_mask(self, seq_len: int, device: torch.device):
        """混合mask：全局token可看全部，局部token只看局部"""
        positions = torch.arange(seq_len, device=device)
        relative_pos = positions.unsqueeze(0) - positions.unsqueeze(1)
        
        # 窗口内为True
        window_mask = relative_pos.abs() <= (self.window_size // 2)
        
        # 全局位置（前num_global_tokens）可以看全部
        global_indices = torch.arange(self.num_global_tokens, device=device)
        global_mask = torch.zeros(seq_len, seq_len, dtype=torch.bool, device=device)
        for idx in global_indices:
            global_mask[idx] = True
            global_mask[:, idx] = True
        
        # 合并
        mask = window_mask | global_mask
        return mask.unsqueeze(0).unsqueeze(0)
