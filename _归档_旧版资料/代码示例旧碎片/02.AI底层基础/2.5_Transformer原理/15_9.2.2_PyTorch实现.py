import torch
import torch.nn as nn
import math

class ALiBiAttention(nn.Module):
    """ALiBi (Attention with Linear Biases) 实现
    
    核心思想：相对位置越远，注意力分数衰减越严重
    """
    def __init__(self, embed_size, heads, dropout=0.1):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        
        self.Wq = nn.Linear(embed_size, embed_size)
        self.Wk = nn.Linear(embed_size, embed_size)
        self.Wv = nn.Linear(embed_size, embed_size)
        self.Wo = nn.Linear(embed_size, embed_size)
        
        self.dropout = nn.Dropout(dropout)
        
        # 初始化ALiBi斜率
        self._init_alibi_slopes()
    
    def _init_alibi_slopes(self):
        """初始化ALiBi斜率
        
        斜率计算方式：基于2^(-8/n)规律，其中n是头数
        """
        n = self.heads
        
        # 方法1: 2^(-8/n) 几何级数
        # slopes = [2^(-8/n), 2^(-16/n), ..., 2^(-8)]
        def get_alibi_slopes(n):
            def get_slopes_power_of_2(n):
                start = 2 ** (-(2 ** -(math.log2(n) - 3)))
                ratio = start
                return [start * ratio ** i for i in range(n)]
            
            if math.log2(n).is_integer():
                return get_slopes_power_of_2(n)
            else:
                closest_power_of_2 = 2 ** math.floor(math.log2(n))
                return (
                    get_slopes_power_of_2(closest_power_of_2) +
                    get_alibi_slopes(2 * closest_power_of_2)[0::2][:n - closest_power_of_2]
                )
        
        slopes = get_alibi_slopes(n)
        self.register_buffer('alibi_slopes', 
                            torch.tensor(slopes, dtype=torch.float32))
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        # 投影到Q, K, V
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        K = self.Wk(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        V = self.Wv(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        
        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        # 创建ALiBi偏置矩阵
        # 形状: (1, heads, seq_len, seq_len)
        alibi_bias = self._create_alibi_bias(seq_len, Q.device)
        
        # 应用ALiBi偏置
        scores = scores + alibi_bias
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-1e9'))
        
        attn_weights = torch.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        output = torch.matmul(attn_weights, V)
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        
        return self.Wo(output), attn_weights
    
    def _create_alibi_bias(self, seq_len, device):
        """创建ALiBi偏置矩阵
        
        偏置公式: -slope * |i - j|
        """
        # 创建相对位置矩阵
        # positions: (seq_len,)
        positions = torch.arange(seq_len, device=device)
        # relative_positions: (seq_len, seq_len)
        relative_positions = positions.unsqueeze(0) - positions.unsqueeze(1)
        # 取绝对值: |i - j|
        relative_positions = torch.abs(relative_positions).float()
        
        # 扩展到多头: (1, heads, seq_len, seq_len)
        # alibi_slopes: (heads,)
        alibi_bias = -self.alibi_slopes.view(1, self.heads, 1, 1) * relative_positions.unsqueeze(0).unsqueeze(0)
        
        return alibi_bias
