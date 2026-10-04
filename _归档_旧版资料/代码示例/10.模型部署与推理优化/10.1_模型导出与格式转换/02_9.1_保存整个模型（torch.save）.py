import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块

class DemoModel(nn.Module):
    """3. 示例模型类，用于演示保存和加载流程"""
    
    def __init__(self):
        """4. 模型初始化方法，定义网络结构"""
        super(DemoModel, self).__init__()  # 5. 调用父类构造函数
        # 6. 定义一个简单的两层神经网络
        self.fc1 = nn.Linear(784, 256)  # 7. 输入层到隐藏层
        self.relu = nn.ReLU()           # 8. ReLU激活函数
        self.fc2 = nn.Linear(256, 10)   # 9. 隐藏层到输出层
        self.softmax = nn.Softmax(dim=1)  # 10. Softmax分类层
    
    def forward(self, x):
        """11. 前向传播方法
        
        参数:
            x: 输入张量，形状为(batch_size, 784)
        返回:
            输出张量，形状为(batch_size, 10)，表示10个类别的概率分布
        """
        x = x.view(-1, 784)             # 12. 将输入展平为一维向量
        x = self.fc1(x)                 # 13. 第一个全连接层
        x = self.relu(x)                # 14. 激活函数
        x = self.fc2(x)                 # 15. 输出层
        x = self.softmax(x)             # 16. 转换为概率分布
        return x

def save_entire_model():
    """17. 演示如何保存整个模型
    
    保存整个模型会将模型的结构定义和参数权重一起保存。
    优点：加载简单，一条语句即可
    缺点：依赖保存时的类定义和代码结构，代码改动后可能无法加载
    """
    # 18. 创建模型实例并初始化权重
    model = DemoModel()
    
    # 19. 假设已经有训练好的权重，这里可以加载预训练权重
    # model.load_state_dict(torch.load('weights.pth'))
    
    # 20. 使用torch.save保存整个模型
    # 第一个参数是模型对象，第二个参数是保存路径
    # '.pth' 或 '.pt' 是PyTorch模型常用的文件扩展名
    torch.save(model, 'entire_model.pth')
    print("✅ 整个模型已保存到 entire_model.pth")

def load_entire_model():
    """21. 演示如何加载整个模型
    
    加载整个模型不需要重新定义模型类，直接从文件加载即可。
    注意：加载时需要确保模型类定义在当前作用域中可用。
    """
    # 22. 直接使用torch.load加载模型
    # 返回的是模型对象，可以直接用于推理
    model = torch.load('entire_model.pth')
    model.eval()                        # 23. 设置为评估模式
    
    # 24. 使用模型进行推理测试
    # 创建一个随机输入进行测试
    test_input = torch.randn(1, 1, 28, 28)  # 25. 模拟MNIST图像输入
    with torch.no_grad():               # 26. 禁用梯度计算，提高推理效率
        output = model(test_input)
    
    print(f"模型输出形状: {output.shape}")  # 27. 应该是(1, 10)
    return model
