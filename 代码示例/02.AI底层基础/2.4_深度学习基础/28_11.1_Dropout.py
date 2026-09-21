import torch
import torch.nn as nn
import torch.nn.functional as F

# 标准Dropout
class DropoutNetwork(nn.Module):
    """使用Dropout的全连接网络"""
    def __init__(self, input_dim, hidden_dim, output_dim, dropout_rate=0.5):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(p=dropout_rate)  # p: 丢弃概率
    
    def forward(self, x):
        x = F.relu(self.dropout(self.fc1(x)))  # 在激活函数后应用Dropout
        x = F.relu(self.dropout(self.fc2(x)))
        x = self.fc3(x)  # 输出层通常不Dropout
        return x

# Dropout原理可视化
def dropout_visualization():
    """展示Dropout如何工作"""
    import matplotlib.pyplot as plt
    
    # 模拟一个简单的Dropout过程
    torch.manual_seed(42)
    dropout = nn.Dropout(p=0.5)
    
    # 输入张量
    x = torch.ones(1, 10)
    
    # 训练模式下，每次调用dropout结果不同
    dropout.train()
    print("训练模式（多次调用）:")
    for i in range(5):
        output = dropout(x)
        print(f"  第{i+1}次: {output.squeeze()[:5].tolist()}...")  # 显示前5个
    
    # 评估模式下，不进行dropout
    dropout.eval()
    output = dropout(x)
    print(f"\n评估模式: {output.squeeze()[:5].tolist()}...")

dropout_visualization()

# 实现自定义Dropout（理解原理）
class CustomDropout(nn.Module):
    """手动实现Dropout层"""
    def __init__(self, p=0.5):
        super().__init__()
        self.p = p
    
    def forward(self, x):
        if self.training:
            # 生成与x形状相同的随机mask
            mask = torch.rand_like(x) > self.p
            # 将被丢弃的位置设为0，并缩放保留的值（保持期望不变）
            return x * mask / (1 - self.p)
        else:
            return x
