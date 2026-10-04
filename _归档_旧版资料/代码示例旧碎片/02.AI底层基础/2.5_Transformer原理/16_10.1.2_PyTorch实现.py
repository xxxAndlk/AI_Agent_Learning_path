import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple

class KVCacheManager:
    """KV Cache管理器
    
    存储和更新推理过程中的Key-Value缓存
    """
    def __init__(self, max_length: int = 4096):
        self.max_length = max_length
        self.k_cache: Optional[torch.Tensor] = None
        self.v_cache: Optional[torch.Tensor] = None
        self.cache_length = 0
    
    def update(self, k: torch.Tensor, v: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        更新缓存
        
        参数:
            k: 当前步的Key (batch, heads, 1, head_dim)
            v: 当前步的Value (batch, heads, 1, head_dim)
        返回:
            拼接后的完整K, V
        """
        batch_size, heads, seq_len, head_dim = k.shape
        
        if self.k_cache is None:
            # 首次初始化
            self.k_cache = k
            self.v_cache = v
        else:
            # 拼接历史缓存
            self.k_cache = torch.cat([self.k_cache, k], dim=2)
            self.v_cache = torch.cat([self.v_cache, v], dim=2)
        
        # 缓存长度限制（可选）
        if self.k_cache.size(2) > self.max_length:
            self.k_cache = self.k_cache[:, :, -self.max_length:, :]
            self.v_cache = self.v_cache[:, :, -self.max_length:, :]
        
        self.cache_length = self.k_cache.size(2)
        return self.k_cache, self.v_cache
    
    def get(self) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor]]:
        """获取当前缓存"""
        return self.k_cache, self.v_cache
    
    def reset(self):
        """重置缓存"""
        self.k_cache = None
        self.v_cache = None
        self.cache_length = 0


class CachedAttention(nn.Module):
    """支持KV Cache的注意力机制"""
    
    def __init__(self, embed_size: int, heads: int):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        
        self.Wq = nn.Linear(embed_size, embed_size)
        self.Wk = nn.Linear(embed_size, embed_size)
        self.Wv = nn.Linear(embed_size, embed_size)
        self.Wo = nn.Linear(embed_size, embed_size)
    
    def forward(
        self, 
        x: torch.Tensor, 
        past_kv: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        use_cache: bool = False
    ):
        """
        参数:
            x: 输入张量 (batch, seq_len, embed_size)
            past_kv: 过去的K, V缓存
            use_cache: 是否使用/更新缓存
        返回:
            output: 注意力输出
            present_kv: 当前的K, V（用于缓存）
        """
        batch_size, seq_len, _ = x.shape
        
        # 投影
        Q = self.Wq(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        K = self.Wk(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        V = self.Wv(x).view(batch_size, seq_len, self.heads, self.head_dim).transpose(1, 2)
        
        if use_cache and past_kv is not None:
            # 拼接历史缓存
            past_k, past_v = past_kv
            K = torch.cat([past_k, K], dim=2)
            V = torch.cat([past_v, V], dim=2)
        
        # 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        
        # 因果掩码（只对当前序列应用）
        if seq_len > 1:
            seq_len_total = K.size(2)
            causal_mask = torch.tril(
                torch.ones(seq_len_total, seq_len_total, 
                          device=Q.device, dtype=torch.bool)
            )
            scores = scores.masked_fill(~causal_mask, float('-1e9'))
        
        attn_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        output = self.Wo(output)
        
        if use_cache:
            # 返回当前的K, V供后续使用
            return output, (K, V)
        return output, None


class CachedTransformerLayer(nn.Module):
    """支持KV Cache的Transformer层"""
    
    def __init__(self, embed_size: int, heads: int, ff_dim: int):
        super().__init__()
        self.attention = CachedAttention(embed_size, heads)
        self.norm1 = nn.LayerNorm(embed_size)
        self.norm2 = nn.LayerNorm(embed_size)
        
        self.ffn = nn.Sequential(
            nn.Linear(embed_size, ff_dim),
            nn.GELU(),
            nn.Linear(ff_dim, embed_size)
        )
    
    def forward(
        self, 
        x: torch.Tensor, 
        past_kv: Optional[Tuple] = None,
        use_cache: bool = False
    ):
        # 自注意力 + 残差
        attn_output, present_kv = self.attention(
            self.norm1(x), past_kv, use_cache
        )
        x = x + attn_output
        
        # 前馈网络 + 残差
        x = x + self.ffn(self.norm2(x))
        
        return x, present_kv


# 推理示例
def generate_with_cache(
    model: nn.Module,
    tokenizer,
    prompt: str,
    max_length: int = 100,
    temperature: float = 1.0
):
    """使用KV Cache加速的文本生成"""
    
    # 编码输入
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    input_ids = input_ids.to(next(model.parameters()).device)
    
    past_kv = None  # 初始缓存为空
    generated = input_ids.clone()
    
    model.eval()
    with torch.no_grad():
        for _ in range(max_length):
            # 只处理最后一个token
            current_ids = generated[:, -1:]
            
            # 前向传播（使用缓存）
            outputs, past_kv = model(current_ids, past_kv=past_kv, use_cache=True)
            
            # 获取下一个token
            logits = outputs[:, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            generated = torch.cat([generated, next_token], dim=1)
            
            # 遇到EOS停止
            if next_token.item() == tokenizer.eos_token_id:
                break
    
    return tokenizer.decode(generated[0], skip_special_tokens=True)
