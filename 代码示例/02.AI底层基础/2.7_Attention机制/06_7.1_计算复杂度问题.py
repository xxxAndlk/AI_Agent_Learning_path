# 问题：序列长度增加，计算量和内存平方增长
# n=512: 注意力矩阵 262K 元素
# n=4096: 注意力矩阵 16M 元素 (64倍)
# n=16384: 注意力矩阵 268M 元素 (1024倍)

# 解决方案1：稀疏注意力
class SparseAttention(nn.Module):
    """只计算局部窗口内的注意力"""
    def __init__(self, window_size=256):
        super().__init__()
        self.window_size = window_size
    
    def forward(self, Q, K, V):
        seq_len = Q.shape[2]
        output = []
        
        for i in range(seq_len):
            start = max(0, i - self.window_size // 2)
            end = min(seq_len, i + self.window_size // 2 + 1)
            
            # 只计算窗口内的注意力
            local_Q = Q[:, :, i:i+1, :]
            local_K = K[:, :, start:end, :]
            local_V = V[:, :, start:end, :]
            
            scores = torch.matmul(local_Q, local_K.transpose(-2, -1))
            weights = F.softmax(scores, dim=-1)
            output.append(torch.matmul(weights, local_V))
        
        return torch.cat(output, dim=2)

# 解决方案2：Flash Attention（推荐）
# PyTorch 2.0+ 内置支持
with torch.backends.cuda.sdp_kernel(enable_flash=True):
    output = F.scaled_dot_product_attention(Q, K, V)
