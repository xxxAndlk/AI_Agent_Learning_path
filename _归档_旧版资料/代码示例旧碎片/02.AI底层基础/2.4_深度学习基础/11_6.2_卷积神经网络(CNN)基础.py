import torch                        # PyTorch核心库
import torch.nn as nn               # 神经网络模块
import torch.optim as optim         # 优化器
from torchvision import datasets, transforms  # 数据集和数据预处理
from torch.utils.data import DataLoader       # 数据加载器

class SimpleCNN(nn.Module):
    """简单CNN模型：用于MNIST手写数字识别
    
    结构：Conv -> ReLU -> MaxPool -> Conv -> ReLU -> MaxPool -> FC -> ReLU -> FC
    """
    def __init__(self, num_classes=10):
        """
        参数:
            num_classes: 分类类别数（MNIST有10个数字0-9）
        """
        super().__init__()
        # 卷积层：提取图像特征
        self.conv_layers = nn.Sequential(
            # 第一层卷积：1通道输入 -> 16通道输出，3x3卷积核，填充1保持尺寸
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),                       # 激活函数
            nn.MaxPool2d(kernel_size=2, stride=2),  # 2x2最大池化，尺寸减半
            # 第二层卷积：16通道 -> 32通道
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)   # 再次池化
        )
        # 全连接层：分类
        self.fc_layers = nn.Sequential(
            # 经过两次池化，28x28 -> 14x14 -> 7x7，32通道，共32*7*7个特征
            nn.Linear(32 * 7 * 7, 128),     # 降维到128
            nn.ReLU(),
            nn.Linear(128, num_classes)     # 输出层：10个类别
        )
    
    def forward(self, x):
        """前向传播"""
        x = self.conv_layers(x)           # 通过卷积层提取特征
        # view改变张量形状：(batch_size, 32, 7, 7) -> (batch_size, 32*7*7)
        x = x.view(x.size(0), -1)
        x = self.fc_layers(x)             # 通过全连接层分类
        return x

def train_cnn():
    """CNN训练流程"""
    # 数据预处理：转为张量并标准化
    # MNIST数据集均值为0.1307，标准差为0.3081（预计算的统计值）
    transform = transforms.Compose([
        transforms.ToTensor(),           # 转为PyTorch张量，并归一化到[0,1]
        transforms.Normalize((0.1307,), (0.3081,))  # 标准化
    ])
    
    # 加载MNIST数据集（手写数字0-9，28x28灰度图像）
    train_dataset = datasets.MNIST(root="./data", train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root="./data", train=False, download=True, transform=transform)
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)
    
    # 选择设备：优先使用GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN().to(device)      # 实例化模型并移到设备
    criterion = nn.CrossEntropyLoss()   # 交叉熵损失（分类任务）
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # Adam优化器
    
    epochs = 5                          # 训练5轮
    for epoch in range(epochs):
        model.train()                   # 训练模式
        total_loss = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)  # 数据移到设备
            optimizer.zero_grad()       # 清空梯度
            output = model(data)        # 前向传播
            loss = criterion(output, target)  # 计算损失
            loss.backward()             # 反向传播
            optimizer.step()            # 更新参数
            total_loss += loss.item()
        print(f"Epoch [{epoch+1}/{epochs}], 平均Loss: {total_loss/len(train_loader):.4f}")
    
    # 测试模型
    model.eval()                        # 评估模式
    correct = 0                         # 正确预测数
    total = 0                           # 总样本数
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)        # 前向传播
            _, predicted = torch.max(output.data, 1)  # 取概率最大的类别
            total += target.size(0)     # 累加样本数
            correct += (predicted == target).sum().item()  # 累加正确数
    print(f"\n测试集准确率: {100 * correct / total:.2f}%")

if __name__ == "__main__":
    train_cnn()
