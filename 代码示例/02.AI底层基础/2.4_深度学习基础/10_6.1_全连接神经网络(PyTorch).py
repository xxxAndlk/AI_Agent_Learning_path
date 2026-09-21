import torch                        # PyTorch核心库
import torch.nn as nn               # 神经网络模块
import torch.optim as optim         # 优化器模块
from torch.utils.data import DataLoader, TensorDataset  # 数据加载工具

class SimpleNN(nn.Module):
    """简单的全连接神经网络
    
    结构: 输入 -> Linear -> ReLU -> Dropout -> Linear -> ReLU -> Linear(输出)
    """
    def __init__(self, input_size=10, hidden_size=64, output_size=1):
        """初始化网络层
        
        参数:
            input_size: 输入特征维度
            hidden_size: 隐藏层神经元数量
            output_size: 输出维度
        """
        super().__init__()            # 调用父类构造函数
        # 使用nn.Sequential按顺序组织网络层
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),  # 第一层：输入到隐藏层
            nn.ReLU(),                           # ReLU激活函数：f(x)=max(0,x)
            nn.Dropout(0.2),                     # Dropout：随机丢弃20%神经元防止过拟合
            nn.Linear(hidden_size, hidden_size//2),  # 第二层：隐藏层到更小的隐藏层
            nn.ReLU(),                           # ReLU激活
            nn.Linear(hidden_size//2, output_size)   # 输出层
        )
    
    def forward(self, x):
        """前向传播：定义数据流经网络的方式"""
        return self.layers(x)         # 数据依次通过所有层

def train_nn():
    """训练神经网络的完整流程"""
    torch.manual_seed(42)             # 设置随机种子保证可复现
    
    # 生成合成数据：输入X，目标y = sum(X) + 噪声
    X = torch.randn(1000, 10)         # 1000个样本，每个10个特征
    y = torch.sum(X, dim=1, keepdim=True) + torch.randn(1000, 1) * 0.1
    
    # 划分训练集(80%)和测试集(20%)
    X_train, X_test = X[:800], X[800:]
    y_train, y_test = y[:800], y[800:]
    
    # 创建数据加载器，batch_size=32表示每次处理32个样本
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    
    model = SimpleNN()                # 实例化模型
    criterion = nn.MSELoss()          # 均方误差损失函数（用于回归任务）
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # Adam优化器
    
    epochs = 50                       # 训练轮数
    model.train()                     # 设置训练模式（启用Dropout等）
    for epoch in range(epochs):
        total_loss = 0                # 累加每轮损失
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()     # 清空梯度（防止累积）
            outputs = model(batch_X)  # 前向传播得到预测值
            loss = criterion(outputs, batch_y)  # 计算损失
            loss.backward()           # 反向传播计算梯度
            optimizer.step()          # 更新模型参数
            total_loss += loss.item() # 累加损失
        # 每10轮打印一次平均损失
        if (epoch+1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], 平均Loss: {total_loss/len(train_loader):.4f}")
    
    # 测试模型
    model.eval()                      # 设置评估模式（禁用Dropout）
    with torch.no_grad():             # 禁用梯度计算（节省内存）
        test_pred = model(X_test)     # 测试集预测
        test_loss = criterion(test_pred, y_test)
        print(f"\n测试集Loss: {test_loss.item():.4f}")

if __name__ == "__main__":
    train_nn()                        # 运行训练
