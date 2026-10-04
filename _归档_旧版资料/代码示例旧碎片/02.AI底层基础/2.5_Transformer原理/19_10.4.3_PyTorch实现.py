import torch
import torch.nn as nn
import torch.nn.functional as F

class GQA(nn.Module):
    """Grouped Query Attention (GQA)
    
    参数:
        embed_size: 嵌入维度
        heads: Query头数
        kv_heads: Key/Value头数（必须能被heads整除）
    """
    
    def __init__(self, embed_size: int, heads: int, kv_heads: int):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.kv_heads = kv_heads
        self.head_dim = embed_size // heads
        self.kv_head_dim = embed_size // kv_heads
        
        # Query: 每头独立
        self.Wq = nn.Linear(embed_size, embed_size)
        
        # Key/Value: 头数少于Query，可共享
        self.Wk = nn.Linear(embed_size, kv_heads * self.kv_head_dim)
        self.Wv = nn.Linear(embed_size, kv_heads * self.kv_head_dim)
        
        self.Wo = nn.Linear(embed_size, embed_size)
        
        # 确保heads能被kv_heads整除
        assert heads % kv_heads == 0, "heads must be divisible by kv_heads"
        self.group_size = heads // kv_heads
    
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None):
        batch_size, seq_len, _ = x.shape
        
        # 投影Q
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim)
        Q = Q.transpose(1, 2)  # (batch, heads, seq_len, head_dim)
        
        # 投影K和V（头数更少）
        K = self.Wk(x).view(batch_size, seq_len, self.kv_heads, self.kv_head_dim)
        V = self.Wv(x).view(batch_size, seq_len, self.kv_heads, self.kv_head_dim)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)  # (batch, kv_heads, seq_len, kv_head_dim)
        
        # 将K, V扩展到与Q相同的头数
        # 方法：每组K, V复制给group_size个Q头
        K = self._expand_kv(K, self.group_size)
        V = self._expand_kv(V, self.group_size)
        
        # 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-1e9'))
        
        attn_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        return self.Wo(output), attn_weights
    
    def _expand_kv(self, kv: torch.Tensor, group_size: int):
        """将KV头扩展到与Q头相同数量
        
        例如：8个KV头 → 32个Q头（每组4个）
        """
        # kv: (batch, kv_heads, seq_len, kv_head_dim)
        # 扩展: (batch, kv_heads, 1, seq_len, kv_head_dim) → (batch, kv_heads*group_size, seq_len, kv_head_dim)
        kv = kv.unsqueeze(2).expand(-1, -1, group_size, -1, -1)
        kv = kv.contiguous().view(kv.size(0), kv.size(1) * group_size, kv.size(3), kv.size(4))
        return kv


class MQA(nn.Module):
    """Multi-Query Attention (MQA)
    
    GQA的特例：所有Q头共享一组K和V
    """
    
    def __init__(self, embed_size: int, heads: int):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        
        self.Wq = nn.Linear(embed_size, embed_size)
        self.Wk = nn.Linear(embed_size, self.head_dim)  # 只有一个头
        self.Wv = nn.Linear(embed_size, self.head_dim)
        self.Wo = nn.Linear(embed_size, embed_size)
    
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None):
        batch_size, seq_len, _ = x.shape
        
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        K = self.Wk(x).unsqueeze(1)  # (batch, 1, seq_len, head_dim)
        V = self.Wv(x).unsqueeze(1)
        
        # 扩展K, V到所有头
        K = K.expand(-1, self.heads, -1, -1)
        V = V.expand(-1, self.heads, -1, -1)
        
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-1e9'))
        
        attn_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        return self.Wo(output), attn_weights
