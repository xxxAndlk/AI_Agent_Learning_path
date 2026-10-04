class LeNet5(nn.Module):
    """LeNet-5: 早期CNN经典架构
    
    网络结构:
    - Input: 1x32x32 (灰度图像)
    - Conv1: 6个5x5卷积 -> 6x28x28
    - Pool1: 2x2平均池化 -> 6x14x14
    - Conv2: 16个5x5卷积 -> 16x10x10
    - Pool2: 2x2平均池化 -> 16x5x5
    - FC1: 16*5*5 -> 120
    - FC2: 120 -> 84
    - Output: 84 -> 10
    
    特点:
    - 使用平均池化
    - 使用Sigmoid/Tanh激活
    - 参数约6万
    """
    def __init__(self, num_classes=10):
        super().__init__()
        
        # 第一个卷积块
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5, padding=2)  # 保持32x32
        self.avgpool1 = nn.AvgPool2d(kernel_size=2, stride=2)   # 16x16
        
        # 第二个卷积块
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)             # 无填充，16x12x12
        self.avgpool2 = nn.AvgPool2d(kernel_size=2, stride=2)   # 16x6x6
        
        # 全连接层
        # 注意：需要根据实际输入尺寸计算
        self.fc1 = nn.Linear(16 * 6 * 6, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, num_classes)
        
        # 激活函数（LeNet原始使用Sigmoid，现在常用ReLU）
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # 卷积块1
        x = self.relu(self.conv1(x))
        x = self.avgpool1(x)
        
        # 卷积块2
        x = self.relu(self.conv2(x))
        x = self.avgpool2(x)
        
        # 展平
        x = x.view(x.size(0), -1)
        
        # 全连接层
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        
        return x

# 打印网络结构
lenet = LeNet5()
print("LeNet-5 结构:")
print(lenet)
total_params = sum(p.numel() for p in lenet.parameters())
print(f"总参数量: {total_params:,}")
