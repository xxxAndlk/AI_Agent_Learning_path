import torch
import torch.nn.functional as F

class FlashAttention(nn.Module):
    """Flash Attention 实现 - 使用分块计算
    
    这是一个简化版本，实际的Flash Attention需要CUDA kernel优化。
    """
    
    def __init__(self, d_model, num_heads, block_size=128):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.block_size = block_size
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def _flash_attention_core(self, Q, K, V):
        """Flash Attention 核心计算
        
        使用分块在线softmax算法。
        
        复杂度: O(n²d) -> O(nd + n·block_size)
        内存: O(n²) -> O(n·block_size)
        """
        batch_size, num_heads, seq_len, head_dim = Q.shape
        
        # 输出和缩放因子
        output = torch.zeros_like(Q)
        l = torch.zeros(batch_size, num_heads, seq_len, 1, device=Q.device)
        m = torch.full((batch_size, num_heads, seq_len, 1), 
                      float('-inf'), device=Q.device)
        
        # 缩放因子
        scale = math.sqrt(head_dim)
        
        # 将K和V分块
        num_blocks = (seq_len + self.block_size - 1) // self.block_size
        
        # 对每个query块进行处理
        for j in range(num_blocks):
            # 加载当前块的K和V
            start_k = j * self.block_size
            end_k = min(start_k + self.block_size, seq_len)
            K_j = K[:, :, start_k:end_k, :]
            V_j = V[:, :, start_k:end_k, :]
            
            # 计算当前块的注意力分数
            QK = torch.matmul(Q, K_j.transpose(-2, -1)) / scale
            
            # 在线softmax计算
            # m_new = max(m, row_max(QK))
            m_new = torch.maximum(m, QK.max(dim=-1, keepdim=True)[0])
            
            # 重新缩放之前的输出
            # o = o * exp(m - m_new)
            exp_diff = torch.exp(m - m_new)
            output = output * exp_diff
            
            # 累加新的贡献
            # l_new = l + row_sum(exp(QK - m_new))
            s = torch.exp(QK - m_new)
            l_new = l + s.sum(dim=-1, keepdim=True)
            
            # 更新输出: o + exp(QK - m_new) * V_j
            output = output + torch.matmul(s, V_j)
            
            # 更新状态
            m = m_new
            l = l_new
        
        # 最终归一化
        output = output / l
        
        return output
    
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        
        Q = self.W_q(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.W_k(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Flash Attention 核心
        output = self._flash_attention_core(Q, K, V)
        
        # 合并多头
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        output = self.W_o(output)
        
        return output, None


def flash_attention_pytorch(q, k, v, dropout_p=0.0, is_causal=True):
    """使用PyTorch 2.0+内置的Flash Attention
    
    这是生产环境中推荐使用的方式。
    
    Args:
        q: (batch, num_heads, seq_len_q, head_dim)
        k: (batch, num_heads, seq_len_k, head_dim)
        v: (batch, num_heads, seq_len_v, head_dim)
        dropout_p: dropout概率
        is_causal: 是否使用因果掩码
    
    Returns:
        output: 注意力输出
    """
    # 检查是否支持Flash Attention
    if hasattr(F, 'scaled_dot_product_attention'):
        # 使用PyTorch内置的Flash Attention
        output = F.scaled_dot_product_attention(
            q, k, v,
            dropout_p=dropout_p if q.is_cuda else 0.0,
            is_causal=is_causal,
            attn_implementation="flash_attention"  # 需要PyTorch 2.0+
        )
        return output, None
    else:
        raise RuntimeError("需要 PyTorch 2.0+ 支持")


def benchmark_flash_attention():
    """对比标准注意力和Flash Attention"""
    device = torch.device('cuda')
    torch.cuda.set_device(0)
    
    batch_size = 4
    num_heads = 8
    d_model = 512
    seq_len = 2048
    
    # 准备输入
    q = torch.randn(batch_size, num_heads, seq_len, d_model // num_heads, device=device)
    k = torch.randn(batch_size, num_heads, seq_len, d_model // num_heads, device=device)
    v = torch.randn(batch_size, num_heads, seq_len, d_model // num_heads, device=device)
    
    # 预热
    with torch.no_grad():
        for _ in range(3):
            _ = torch.matmul(q, k.transpose(-2, -1))
            _ = F.scaled_dot_product_attention(q, k, v)
    
    torch.cuda.synchronize()
    
    import time
    
    results = {}
    
    # 标准注意力
    start = time.time()
    for _ in range(10):
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(d_model // num_heads)
        attn = F.softmax(scores, dim=-1)
        out = torch.matmul(attn, v)
    torch.cuda.synchronize()
    results['standard'] = (time.time() - start) / 10
    
    # Flash Attention
    start = time.time()
    for _ in range(10):
        out = F.scaled_dot_product_attention(q, k, v, is_causal=False)
    torch.cuda.synchronize()
    results['flash'] = (time.time() - start) / 10
    
    print(f"标准注意力: {results['standard']:.4f}s")
    print(f"Flash Attention: {results['flash']:.4f}s")
    print(f"加速比: {results['standard'] / results['flash']:.2f}x")
    
    return results
