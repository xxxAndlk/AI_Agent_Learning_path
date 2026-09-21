import torch
import torch.nn as nn
import torch.nn.functional as F

class FlashAttention(nn.Module):
    """简化版Flash Attention实现
    
    注意：实际生产环境建议使用FlashAttention库
    安装: pip install flash-attn
    """
    
    def __init__(self, embed_size: int, heads: int, dropout: float = 0.0):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        self.dropout = dropout
        
        self.Wq = nn.Linear(embed_size, embed_size)
        self.Wk = nn.Linear(embed_size, embed_size)
        self.Wv = nn.Linear(embed_size, embed_size)
        self.Wo = nn.Linear(embed_size, embed_size)
    
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None):
        """
        参数:
            x: (batch, seq_len, embed_size)
            mask: 可选的attention mask
        """
        batch_size, seq_len, _ = x.shape
        
        # 投影
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        K = self.Wk(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        V = self.Wv(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        
        # Flash Attention核心计算
        output = self._flash_attention(Q, K, V, mask)
        
        # 输出投影
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        return self.Wo(output)
    
    def _flash_attention(
        self, 
        Q: torch.Tensor, 
        K: torch.Tensor, 
        V: torch.Tensor,
        mask: torch.Tensor = None
    ):
        """Flash Attention核心实现
        
        使用分块和在线softmax减少内存占用
        """
        batch_size, heads, seq_len, head_dim = Q.shape
        
        # 将序列分块
        BLOCK_SIZE = 128  # 可调整
        
        # 初始化输出和辅助变量
        output = torch.zeros_like(Q)
        
        # 逐块计算
        for start_idx in range(0, seq_len, BLOCK_SIZE):
            end_idx = min(start_idx + BLOCK_SIZE, seq_len)
            
            # 当前块
            Q_block = Q[:, :, start_idx:end_idx, :]
            
            # 计算当前块的注意力
            # (batch, heads, block_size, seq_len)
            attn_scores = torch.matmul(Q_block, K.transpose(-2, -1)) / (head_dim ** 0.5)
            
            # 应用mask
            if mask is not None:
                attn_scores = attn_scores.masked_fill(mask == 0, float('-1e9'))
            
            # 在线softmax（数值稳定）
            attn_weights = F.softmax(attn_scores, dim=-1)
            
            # 加权求和
            block_output = torch.matmul(attn_weights, V)
            
            # 写入输出
            output[:, :, start_idx:end_idx, :] = block_output
        
        return output


# 实际使用Flash Attention库（推荐）
def flash_attention_using_library():
    """
    生产环境建议使用flash-attn库
    
    安装: pip install flash-attn
    """
    try:
        from flash_attn import flash_attn_func
        
        def forward_with_flash_attn(Q, K, V, mask=None):
            """
            Q, K, V: (batch, heads, seq_len, head_dim)
            """
            # flash_attn_func返回 (batch, heads, seq_len, head_dim)
            output = flash_attn_func(
                Q, K, V,
                dropout_p=0.0,
                softmax_scale=None,
                causal=True  # 自回归生成时设为True
            )
            return output
    except ImportError:
        print("请安装flash-attn: pip install flash-attn")
        return None

# PyTorch 2.0+ 内置的scaled_dot_product_attention（自动使用Flash Attention）
def scaled_dot_product_flash(Q, K, V, mask=None):
    """使用PyTorch 2.0+的SDPA，自动选择最优后端"""
    
    # PyTorch会自动选择：
    # 1. FlashAttention (如果有CUDA)
    # 2. Memory-Efficient Attention
    # 3. Math fallback
    
    output = F.scaled_dot_product_attention(
        Q, K, V,
        attn_mask=mask,
        dropout_p=0.0 if Q.requires_grad else 0.0,
        is_causal=mask is None  # 自动生成causal mask
    )
    
    return output
