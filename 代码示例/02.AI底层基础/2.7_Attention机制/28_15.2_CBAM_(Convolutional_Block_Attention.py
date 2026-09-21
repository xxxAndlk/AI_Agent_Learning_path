class ChannelAttention(nn.Module):
    """通道注意力模块
    
    使用MaxPool和AvgPool两种方式捕获通道统计信息。
    """
    
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        
        # 共享MLP
        self.mlp = nn.Sequential(
            nn.Conv2d(channels, channels // reduction, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels // reduction, channels, 1, bias=False)
        )
        
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        avg_out = self.mlp(self.avg_pool(x))
        max_out = self.mlp(self.max_pool(x))
        
        # 融合两种pooling的结果
        out = avg_out + max_out
        return self.sigmoid(out)


class SpatialAttention(nn.Module):
    """空间注意力模块
    
    关注"哪里"是最重要的信息。
    """
    
    def __init__(self, kernel_size=7):
        super().__init__()
        # 边缘填充保持尺寸
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # 通道维度的平均和最大池化
        avg_out = x.mean(dim=1, keepdim=True)
        max_out = x.max(dim=1, keepdim=True)[0]
        
        # 拼接
        combined = torch.cat([avg_out, max_out], dim=1)
        
        # 卷积并应用sigmoid
        out = self.conv(combined)
        return self.sigmoid(out)


class CBAM(nn.Module):
    """CBAM (Convolutional Block Attention Module)
    
    依次应用通道注意力和空间注意力。
    
    流程:
    Input -> Channel Attention -> Mul -> Spatial Attention -> Mul -> Output
    """
    
    def __init__(self, channels, reduction=16, kernel_size=7):
        super().__init__()
        self.channel_attention = ChannelAttention(channels, reduction)
        self.spatial_attention = SpatialAttention(kernel_size)
    
    def forward(self, x):
        # 通道注意力
        x = x * self.channel_attention(x)
        
        # 空间注意力
        x = x * self.spatial_attention(x)
        
        return x


# CBAM 在ResNet中的应用
class CBAMResNetBlock(nn.Module):
    """带CBAM的ResNet块"""
    
    def __init__(self, in_channels, out_channels, stride=1, reduction=16):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # CBAM
        self.cbam = CBAM(out_channels, reduction)
        
        # 短路连接
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
        
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        
        # 应用CBAM
        out = self.cbam(out)
        
        # 短路连接
        out += self.shortcut(x)
        out = self.relu(out)
        
        return out
