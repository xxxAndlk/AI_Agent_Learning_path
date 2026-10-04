class ModernNN(nn.Module):
    """现代神经网络模板：包含BatchNorm和Dropout"""
    def __init__(self, input_size, hidden_sizes, output_size, dropout=0.2):
        super().__init__()
        layers = []
        
        # 动态构建隐藏层
        prev_size = input_size
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),  # 批归一化：加速收敛
                nn.ReLU(),
                nn.Dropout(dropout),           # 防止过拟合
            ])
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, output_size))
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)
