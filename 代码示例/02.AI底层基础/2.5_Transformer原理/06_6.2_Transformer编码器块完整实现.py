class TransformerEncoderBlock(nn.Module):
    """Transformer编码器块
    
    结构：多头注意力 -> Add&Norm -> 前馈网络 -> Add&Norm
    
    每个子层都有:
    1. 残差连接 (Residual Connection)
    2. 层归一化 (Layer Normalization)
    
    这种Pre-Norm结构（先归一化再子层）在后续模型中更常用
    """
    def __init__(self, embed_size, heads, forward_expansion, dropout):
        """
        参数:
            embed_size: 嵌入维度
            heads: 注意力头数
            forward_expansion: 前馈网络扩展倍数（通常为4）
            dropout: Dropout概率
        """
        super().__init__()
        # 多头自注意力层
        self.attention = MultiHeadAttention(embed_size, heads)
        
        # 层归一化（Layer Normalization）
        # 对每个样本的特征维度做归一化，稳定训练
        # 与BatchNorm不同，LayerNorm不依赖batch统计量
        self.norm1 = nn.LayerNorm(embed_size)
        self.norm2 = nn.LayerNorm(embed_size)
        
        # 前馈网络（Feed Forward Network）
        # 结构：Linear -> ReLU -> Linear
        # 中间维度扩展forward_expansion倍，再压缩回原维度
        # 这是典型的"瓶颈"结构，增加非线性能力
        self.feed_forward = nn.Sequential(
            nn.Linear(embed_size, forward_expansion * embed_size),
            nn.ReLU(),
            nn.Linear(forward_expansion * embed_size, embed_size)
        )
        
        # Dropout层，防止过拟合
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        """前向传播
        
        参数:
            x: 输入张量 (batch_size, seq_len, embed_size)
            mask: 注意力掩码
        返回:
            经过编码器块处理后的张量
        """
        # 子层1：多头自注意力 + 残差连接 + 层归一化
        # 残差连接（Residual Connection）：将输入加到子层输出上
        # 公式: LayerNorm(x + Sublayer(x))
        # x + self.dropout(...) 是残差连接的核心
        
        # 自注意力：Q=K=V=x，即输入同时作为查询、键、值
        # 这意味着每个位置可以"看到"序列中的所有其他位置
        attn_output, _ = self.attention(x, x, x, mask)  # 自注意力：Q=K=V=x
        x = self.norm1(x + self.dropout(attn_output))   # Add & Norm
        
        # 子层2：前馈网络 + 残差连接 + 层归一化
        # 前馈网络为模型增加非线性变换能力
        # 每个位置独立通过相同的MLP
        ff_output = self.feed_forward(x)                # 前馈网络变换
        x = self.norm2(x + self.dropout(ff_output))     # Add & Norm
        
        return x
