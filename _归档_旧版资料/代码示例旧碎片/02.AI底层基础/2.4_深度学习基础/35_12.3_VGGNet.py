class VGGNet(nn.Module):
    """VGGNet: 使用小卷积核的深层网络
    
    VGG-16结构:
    - 13个卷积层（全部使用3x3卷积）
    - 3个全连接层
    
    核心思想:
    - 两个3x3卷积的感受野等于一个5x5卷积
    - 三个3x3卷积的感受野等于一个7x7卷积
    - 但参数量更少，且非线性更多
    """
    def __init__(self, num_classes=1000, variant='VGG16'):
        super().__init__()
        
        # 配置不同VGG变体
        configs = {
            'VGG11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
            'VGG13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
            'VGG16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
            'VGG19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
        }
        
        config = configs[variant]
        layers = []
        in_channels = 3
        
        # 构建卷积层
        for v in config:
            if v == 'M':
                layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
            else:
                layers.append(nn.Conv2d(in_channels, v, kernel_size=3, padding=1))
                layers.append(nn.ReLU(inplace=True))
                in_channels = v
        
        self.features = nn.Sequential(*layers)
        
        # 全局平均池化（替代原始的全连接层）
        self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
        
        # 全连接层
        self.classifier = nn.Sequential(
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, num_classes),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

# 创建不同版本的VGG
vgg11 = VGGNet(variant='VGG11')
vgg16 = VGGNet(variant='VGG16')
vgg19 = VGGNet(variant='VGG19')

# 计算参数量
def count_params(model):
    return sum(p.numel() for p in model.parameters())

print(f"VGG11 参数量: {count_params(vgg11):,}")
print(f"VGG16 参数量: {count_params(vgg16):,}")
print(f"VGG19 参数量: {count_params(vgg19):,}")
