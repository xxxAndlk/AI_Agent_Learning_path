class LSTMNetwork(nn.Module):
    """LSTM网络
    
    LSTM核心组件:
    - 遗忘门: 决定保留多少上一时刻的状态
    - 输入门: 决定更新多少新信息
    - 输出门: 决定输出多少信息
    """
    def __init__(self, input_size, hidden_size, num_layers=1, dropout=0.1):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=False,  # 双向LSTM
        )
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
    
    def forward(self, x):
        """
        参数:
            x: (batch, seq_len, input_size)
        返回:
            output: (batch, seq_len, hidden_size)
            (h_n, c_n): 最后一个时间步的隐藏状态和细胞状态
        """
        output, (h_n, c_n) = self.lstm(x)
        return output, (h_n, c_n)


class BidirectionalLSTM(nn.Module):
    """双向LSTM
    
    双向LSTM能同时利用过去和未来的上下文信息
    适用于需要完整上下文的任务，如词性标注、语音识别
    """
    def __init__(self, input_size, hidden_size, num_layers=1):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,  # 双向
        )
        
        # 输出层：隐藏状态翻倍（双向）
        self.fc = nn.Linear(hidden_size * 2, 10)
    
    def forward(self, x):
        output, _ = self.lstm(x)
        # 对所有时间步的输出进行预测
        return self.fc(output)


def lstm_detailed():
    """LSTM门控机制详解"""
    
    # 查看PyTorch LSTM的参数
    lstm = nn.LSTM(input_size=10, hidden_size=20, batch_first=True)
    
    # LSTM的权重参数
    for name, param in lstm.named_parameters():
        print(f"{name}: {param.shape}")
    
    # 输出说明:
    # weight_ih_l0: (80, 10) - 输入到隐藏的权重 (4个门 × hidden_size, input_size)
    # weight_hh_l0: (80, 20) - 隐藏到隐藏的权重 (4个门 × hidden_size, hidden_size)
    # bias_ih_l0: (80,) - 输入偏置
    # bias_hh_l0: (80,) - 隐藏偏置
    
    # 80 = 20 * 4，对应4个门:
    # - 遗忘门 (Forget Gate): f_t = σ(W_f·[h_{t-1}, x_t] + b_f)
    # - 输入门 (Input Gate): i_t = σ(W_i·[h_{t-1}, x_t] + b_i)
    # - 候选值 (Candidate Values): C̃_t = tanh(W_C·[h_{t-1}, x_t] + b_C)
    # - 输出门 (Output Gate): o_t = σ(W_o·[h_{t-1}, x_t] + b_o)
    
    # LSTM公式:
    # f_t = σ(W_f·[h_{t-1}, x_t] + b_f)
    # i_t = σ(W_i·[h_{t-1}, x_t] + b_i)
    # C̃_t = tanh(W_C·[h_{t-1}, x_t] + b_C)
    # C_t = f_t * C_{t-1} + i_t * C̃_t
    # o_t = σ(W_o·[h_{t-1}, x_t] + b_o)
    # h_t = o_t * tanh(C_t)
