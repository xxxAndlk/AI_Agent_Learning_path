class GRUNetwork(nn.Module):
    """GRU网络
    
    GRU核心组件（2个门，比LSTM少1个）:
    - 更新门: 决定保留多少过去的状态
    - 重置门: 决定忽略多少过去的信息
    
    优势: 参数量更少，训练更快
    劣势: 在某些复杂任务上可能不如LSTM
    """
    def __init__(self, input_size, hidden_size, num_layers=1):
        super().__init__()
        
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=False,
        )
        
        self.fc = nn.Linear(hidden_size, 10)
    
    def forward(self, x):
        output, hidden = self.gru(x)
        # 使用最后一个时间步的输出进行分类
        last_output = output[:, -1, :]  # (batch, hidden_size)
        return self.fc(last_output)


def gru_vs_lstm():
    """GRU vs LSTM 对比"""
    
    input_size = 100
    hidden_size = 256
    seq_len = 50
    batch = 32
    
    # 测试不同RNN单元的参数数量
    rnn_cells = {
        'RNN': nn.RNNCell(input_size, hidden_size),
        'LSTM': nn.LSTMCell(input_size, hidden_size),
        'GRU': nn.GRUCell(input_size, hidden_size),
    }
    
    for name, cell in rnn_cells.items():
        params = sum(p.numel() for p in cell.parameters())
        print(f"{name} 参数数量: {params:,}")
    
    # 典型结果（input=100, hidden=256）:
    # RNN: 约23,000
    # LSTM: 约230,000 (4个门)
    # GRU: 约180,000 (3个门)
