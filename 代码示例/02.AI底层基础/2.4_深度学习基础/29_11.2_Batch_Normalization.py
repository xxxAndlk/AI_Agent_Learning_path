# BatchNorm 1D 用于全连接层
class BatchNormMLP(nn.Module):
    """使用BatchNorm的全连接网络"""
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),  # 1D BatchNorm
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.layers(x)

# BatchNorm 2D 用于卷积神经网络
class BatchNormCNN(nn.Module):
    """使用BatchNorm的CNN"""
    def __init__(self, num_classes=10):
        super().__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),  # 2D BatchNorm，注意通道数要匹配
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.fc = nn.Linear(64 * 8 * 8, num_classes)
    
    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

# BatchNorm 原理和最佳实践
def batchnorm_best_practices():
    """BatchNorm最佳实践"""
    
    # 1. BatchNorm在训练和评估模式行为不同
    bn = nn.BatchNorm2d(32)
    
    # 训练模式：使用当前batch的统计量
    bn.train()
    x = torch.randn(8, 32, 16, 16)
    out_train = bn(x)
    
    # 评估模式：使用训练时累积的统计量
    bn.eval()
    out_eval = bn(x)
    
    # 2. BatchNorm的关键超参数
    bn_config = nn.BatchNorm2d(
        num_features=32,
        momentum=0.1,       # 统计量的移动平均系数（默认0.1）
        # 较小的momentum使统计量更新更快
        # 注意：PyTorch的momentum含义与论文相反
        # 实际使用时: running_mean = (1-momentum) * running_mean + momentum * batch_mean
        eps=1e-5,           # 防止除零
        affine=True,        # 是否使用可学习参数γ和β
        track_running_stats=True  # 是否跟踪运行统计量
    )
    
    # 3. BatchNorm的局限性
    # - 依赖batch size，batch太小时效果差
    # - 不适用于变长序列（RNN）
    # - 训练和推理行为不一致
