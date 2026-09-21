import torch
import torch.nn as nn
import math

class RoPE(nn.Module):
    """旋转位置编码实现"""
    
    def __init__(self, dim, max_seq_len=512):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len
        
        # 预计算旋转角度
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        
        # 预计算旋转矩阵的缓存
        self._set_cos_sin_cache(max_seq_len)
    
    def _set_cos_sin_cache(self, seq_len):
        """预计算cos和sin值"""
        self.max_seq_len_cached = seq_len
        t = torch.arange(seq_len, device=self.inv_freq.device)
        
        # 外积得到完整频率矩阵 (seq_len, dim//2)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        
        # 拼接cos和sin (seq_len, dim)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer("cos_cached", emb.cos(), persistent=False)
        self.register_buffer("sin_cached", emb.sin(), persistent=False)
    
    def forward(self, x, seq_len=None):
        """应用RoPE
        
        参数:
            x: 输入tensor (batch, seq_len, dim)
            seq_len: 序列长度
        """
        if seq_len is None:
            seq_len = x.shape[1]
        
        # 确保缓存足够长
        if seq_len > self.max_seq_len_cached:
            self._set_cos_sin_cache(seq_len)
        
        # 提取cos和sin
        cos = self.cos_cached[:seq_len]
        sin = self.sin_cached[:seq_len]
        
        # 旋转操作
        return self._rotate_half(x, cos, sin)
    
    def _rotate_half(self, x, cos, sin):
        """旋转半个维度"""
        # 将x分为前后两半
        x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
        
        # 应用旋转公式
        # x' = x1*cos - x2*sin
        #    x2*cos + x1*sin
        return torch.cat([
            x1 * cos - x2 * sin,
            x2 * cos + x1 * sin
        ], dim=-1)

# 测试RoPE
def test_rope():
    """测试RoPE实现"""
    
    # 配置
    batch_size = 2
    seq_len = 10
    num_heads = 8
    head_dim = 64
    dim = num_heads * head_dim
    
    # 创建输入
    x = torch.randn(batch_size, seq_len, dim)
    
    # 应用RoPE
    rope = RoPE(head_dim, max_seq_len=512)
    x_rope = rope(x)
    
    print(f"输入形状: {x.shape}")
    print(f"RoPE输出形状: {x_rope.shape}")
    
    # 验证相对位置特性
    # 位置i和位置j的attention应该与位置i+j有关
    pos_0 = x_rope[0, 0, :head_dim]
    pos_1 = x_rope[0, 1, :head_dim]
    pos_2 = x_rope[0, 2, :head_dim]
    
    # 检查旋转角度
    print(f"位置0旋转角度范围: [{pos_0.min():.3f}, {pos_0.max():.3f}]")
    print(f"位置1旋转角度范围: [{pos_1.min():.3f}, {pos_1.max():.3f}]")

test_rope()
