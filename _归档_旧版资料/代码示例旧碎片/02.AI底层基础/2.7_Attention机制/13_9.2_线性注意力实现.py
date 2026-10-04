import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class LinearAttention(nn.Module):
    """线性注意力机制 - O(n)复杂度
    
    通过核函数近似消除Softmax，将O(n²)降低到O(n)。
    """
    
    def __init__(self, d_model, num_heads=8, kernel_type='relu'):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.kernel_type = kernel_type
        
        # 投影层
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        # 核函数参数（用于随机特征映射）
        if kernel_type == 'relu':
            self.kernel_proj = nn.Linear(self.head_dim, self.head_dim * 2)
    
    def _apply_kernel(self, x):
        """应用核函数映射 φ(x)"""
        if self.kernel_type == 'linear':
            return x
        elif self.kernel_type == 'relu':
            # ReLU随机特征映射 (RFA - Rectified Feature Attention)
            x = self.kernel_proj(x)
            x1, x2 = x.chunk(2, dim=-1)
            return F.relu(x1) * x2.abs().sqrt()
        elif self.kernel_type == 'elu':
            x = self.kernel_proj(x)
            return F.elu(x) + 1
        else:
            return x
    
    def forward(self, Q, K, V, mask=None):
        """
        Q, K, V: (batch, num_heads, seq_len, head_dim)
        """
        batch_size = Q.shape[0]
        seq_len = Q.shape[2]
        
        # 线性投影
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # 应用核函数
        Q_prime = self._apply_kernel(Q)
        K_prime = self._apply_kernel(K)
        
        # 线性注意力核心计算
        # KV_sum: Σⱼ φ(kⱼ) · vⱼ
        KV = torch.einsum('bhnd,bhne->bhde', K_prime, V)  # (batch, heads, dim, dim)
        
        # Z: Σⱼ φ(kⱼ) 用于归一化
        K_sum = K_prime.sum(dim=2)  # (batch, heads, head_dim)
        
        # 计算输出
        # output = φ(qᵢ)^T · (Σⱼ φ(kⱼ) · vⱼ)
        output = torch.einsum('bhnd,bhde->bhnf', Q_prime, KV)  # (batch, heads, seq, head_dim)
        
        # 归一化
        # 防止除零，添加小常数
        Z = torch.einsum('bhd,bhd->bh', Q_prime, K_sum).unsqueeze(-1)
        output = output / (Z + 1e-8)
        
        # 合并多头并输出投影
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.W_o(output)
        
        return output, None


class LinearAttentionSimple(nn.Module):
    """简化版线性注意力 - 状态空间形式
    
    使用前缀和技巧实现真正的O(n)复杂度
    """
    
    def __init__(self, d_model):
        super().__init__()
        self.d_model = d_model
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        """
        x: (batch, seq_len, d_model)
        """
        batch_size, seq_len, _ = x.shape
        
        Q = self.W_q(x)
        K = self.W_k(x)
        V = self.W_v(x)
        
        # 状态空间形式 - 逐位置计算
        # 使用 cumsum 累积状态
        output = []
        running_KV = torch.zeros(batch_size, self.d_model, device=x.device)
        running_K = torch.zeros(batch_size, self.d_model, device=x.device)
        
        for i in range(seq_len):
            # 更新状态
            running_KV = running_KV + K[:, i] * V[:, i].unsqueeze(-1)
            running_K = running_K + K[:, i]
            
            # 计算当前输出
            # output_i = Q_i · running_KV / (Q_i · running_K)
            denom = (Q[:, i] * running_K).sum(dim=-1, keepdim=True)
            out_i = (Q[:, i].unsqueeze(-1) * running_KV) / (denom + 1e-8)
            output.append(out_i)
        
        output = torch.stack(output, dim=1)
        output = self.W_o(output)
        
        return output, None
