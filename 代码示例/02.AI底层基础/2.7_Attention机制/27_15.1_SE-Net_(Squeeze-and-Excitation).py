class SEBlock(nn.Module):
    """SE (Squeeze-and-Excitation) 注意力模块
    
    核心思想:
    1. Squeeze: 全局平均池化，将空间信息压缩为通道描述符
    2. Excitation: 学习每个通道的权重，实现通道注意力
    
    数学公式:
    s = σ(W₂ · ReLU(W₁ · GAP(x)))
    y = s · x
    """
    
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.channels = channels
        self.reduction = reduction
        
        # Squeeze: 全局平均池化 (无需参数)
        
        # Excitation: 两层全连接
        self.fc1 = nn.Linear(channels, channels // reduction)
        self.fc2 = nn.Linear(channels // reduction, channels)
        
        self.relu = nn.ReLU(inplace=True)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        """
        x: (batch, channels, height, width)
        """
        batch, channels, _, _ = x.shape
        
        # Squeeze: 全局平均池化
        # 输出: (batch, channels)
        gap = x.view(batch, channels, -1).mean(dim=2)
        
        # Excitation: 学习通道权重
        # (batch, channels) -> (batch, channels // r) -> (batch, channels)
        excitation = self.fc1(gap)
        excitation = self.relu(excitation)
        excitation = self.fc2(excitation)
        excitation = self.sigmoid(excitation)
        
        # 重新reshape并应用权重
        excitation = excitation.view(batch, channels, 1, 1)
        output = x * excitation
        
        return output


# 在卷积网络中应用SE块
class SEConvBlock(nn.Module):
    """带SE注意力的卷积块"""
    
    def __init__(self, in_channels, out_channels, kernel_size=3, reduction=16):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, 
                             padding=kernel_size//2)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.se = SEBlock(out_channels, reduction)
    
    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        x = self.se(x)
        return x
