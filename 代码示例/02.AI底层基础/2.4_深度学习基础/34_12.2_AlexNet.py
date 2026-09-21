class AlexNet(nn.Module):
    """AlexNet: 2012年ImageNet冠军
    
    网络结构:
    - Input: 3x227x227 (RGB图像)
    - Conv1: 96个11x11卷积，步长4 -> 96x55x55
    - Pool1: 3x3步长2 -> 96x27x27
    - Conv2: 256个5x5卷积 -> 256x27x27
    - Pool2: 3x3步长2 -> 256x13x13
    - Conv3: 384个3x3卷积 -> 384x13x13
    - Conv4: 384个3x3卷积 -> 384x13x13
    - Conv5: 256个3x3卷积 -> 256x13x13
    - Pool3: 3x3步长2 -> 256x6x6
    - FC1: 256*6*6 -> 4096
    - FC2: 4096 -> 4096
    - Output: 4096 -> 1000
    
    创新点:
    - ReLU激活函数（替代Sigmoid）
    - Dropout正则化
    - GPU并行训练
    - 数据增强
    """
    def __init__(self, num_classes=1000):
        super().__init__()
        
        # 特征提取部分（卷积层）
        self.features = nn.Sequential(
            # Conv1: 11x11卷积，步长4
            nn.Conv2d(3, 96, kernel_size=11, stride=4, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),  # 55x55 -> 27x27
            
            # Conv2: 5x5卷积
            nn.Conv2d(96, 256, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),  # 27x27 -> 13x13
            
            # Conv3: 3x3卷积
            nn.Conv2d(256, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            
            # Conv4: 3x3卷积
            nn.Conv2d(384, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            
            # Conv5: 3x3卷积
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),  # 13x13 -> 6x6
        )
        
        # 分类器部分（全连接层）
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.5),  # Dropout正则化
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

# 简化的现代AlexNet（适配224x224输入）
class ModernAlexNet(nn.Module):
    """简化版AlexNet，适配224x224输入"""
    def __init__(self, num_classes=1000):
        super().__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            
            nn.Conv2d(64, 192, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            
            nn.Conv2d(192, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )
        
        self.avgpool = nn.AdaptiveAvgPool2d((6, 6))  # 全局平均池化
        
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x
