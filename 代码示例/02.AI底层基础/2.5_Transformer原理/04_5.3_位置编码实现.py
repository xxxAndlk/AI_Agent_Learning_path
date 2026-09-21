import math

class PositionalEncoding(nn.Module):
    """
    原始Transformer的正弦/余弦位置编码
    """
    def __init__(self, d_model, max_seq_len=5000, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # 创建位置编码矩阵
        pe = torch.zeros(max_seq_len, d_model)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        
        # 计算分母项
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        
        # 偶数维度用sin，奇数维度用cos
        pe[:, 0::2] = torch.sin(position * div_term)  # 偶数列
        pe[:, 1::2] = torch.cos(position * div_term)  # 奇数列
        
        # 添加batch维度: (1, max_seq_len, d_model)
        pe = pe.unsqueeze(0)
        
        # 注册为buffer，不参与训练
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        """
        x: (batch_size, seq_len, d_model)
        """
        # 将位置编码加到输入上
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)
