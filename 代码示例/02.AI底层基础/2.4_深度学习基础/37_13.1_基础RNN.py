class SimpleRNN(nn.Module):
    """简单RNN实现
    
    RNN核心公式:
    h_t = tanh(W_ih * x_t + b_ih + W_hh * h_{t-1} + b_hh)
    """
    def __init__(self, input_size, hidden_size, num_layers=1, batch_first=True):
        super().__init__()
        
        self.rnn = nn.RNN(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=batch_first,  # 输入形状为 (batch, seq, feature)
            nonlinearity='tanh',       # 激活函数
            dropout=0 if num_layers == 1 else 0.1,  # 多层时使用dropout
        )
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
    
    def forward(self, x):
        """
        参数:
            x: 输入张量 (batch, seq_len, input_size)
        返回:
            output: 所有时间步的输出 (batch, seq_len, hidden_size)
            hidden: 最后时刻的隐藏状态 (num_layers, batch, hidden_size)
        """
        output, hidden = self.rnn(x)
        return output, hidden


def rnn_example():
    """RNN使用示例"""
    # 参数设置
    batch_size = 4
    seq_len = 10
    input_size = 8
    hidden_size = 16
    
    # 创建RNN
    rnn = SimpleRNN(input_size, hidden_size, num_layers=2)
    
    # 模拟输入
    x = torch.randn(batch_size, seq_len, input_size)
    
    # 前向传播
    output, hidden = rnn(x)
    
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {output.shape}")  # (4, 10, 16)
    print(f"隐藏状态形状: {hidden.shape}")  # (2, 4, 16)
