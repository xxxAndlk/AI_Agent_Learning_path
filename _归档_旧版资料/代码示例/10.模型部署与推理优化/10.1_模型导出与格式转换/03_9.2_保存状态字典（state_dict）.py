import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块

class StateDictModel(nn.Module):
    """3. 示例模型类，用于演示state_dict保存方式"""
    
    def __init__(self):
        """4. 模型初始化"""
        super(StateDictModel, self).__init__()
        # 5. 定义一个卷积神经网络用于图像分类
        # 6. 第一个卷积层：1通道输入，32个3x3卷积核
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        # 7. 批量归一化层，加速训练稳定
        self.bn1 = nn.BatchNorm2d(32)
        # 8. 第二个卷积层
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        # 9. 池化层，减小特征图尺寸
        self.pool = nn.MaxPool2d(2, 2)
        # 10. 全连接层
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        # 11. Dropout层，防止过拟合
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        """12. 前向传播方法
        
        参数:
            x: 输入张量，形状为(batch_size, 1, 28, 28)
        返回:
            output: 输出张量，形状为(batch_size, 10)
        """
        # 13. 第一个卷积块：卷积 -> 批归一化 -> ReLU -> 池化
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))
        # 14. 第二个卷积块
        x = self.pool(torch.relu(self.bn2(self.conv2(x))))
        # 15. 展平特征图
        x = x.view(-1, 64 * 7 * 7)
        # 16. 全连接层
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

def save_model_state_dict():
    """17. 演示保存模型state_dict
    
    state_dict是一个Python字典，键是参数名称，值是参数张量。
    保存state_dict的好处：
    1. 文件体积更小（不包含模型结构信息）
    2. 加载时更灵活，可以加载到不同结构的模型中
    3. 代码重构后，只要参数名不变就能正常加载
    """
    # 18. 创建模型实例
    model = StateDictModel()
    
    # 19. 查看state_dict的内容
    # 打印出所有参数层的名称和形状
    print("=== 模型state_dict内容 ===")
    for key, value in model.state_dict().items():
        print(f"{key}: {value.shape}")
    
    # 20. 保存state_dict
    # 使用torch.save保存state_dict字典
    torch.save(model.state_dict(), 'model_state_dict.pth')
    print("✅ 模型state_dict已保存到 model_state_dict.pth")
    
    # 21. 返回模型，供后续加载演示使用
    return model

def load_model_state_dict():
    """22. 演示加载模型state_dict
    
    加载state_dict需要先创建模型实例，然后使用load_state_dict方法加载。
    需要注意strict参数的使用。
    """
    # 23. 创建模型实例（结构必须与保存时一致）
    model = StateDictModel()
    
    # 24. 加载state_dict
    # strict=True（默认）要求保存的键与模型参数完全匹配
    # strict=False允许部分匹配，用于加载部分参数或结构略有不同的模型
    state_dict = torch.load('model_state_dict.pth')
    model.load_state_dict(state_dict, strict=True)
    
    model.eval()                        # 25. 设置为评估模式
    print("✅ 模型state_dict已加载")
    
    # 26. 验证加载成功，进行一次推理
    test_input = torch.randn(1, 1, 28, 28)
    with torch.no_grad():
        output = model(test_input)
    print(f"测试推理输出形状: {output.shape}")
    
    return model

def save_checkpoint():
    """27. 演示保存检查点（checkpoint）
    
    检查点不仅包含模型参数，还包含优化器状态、epoch、loss等信息。
    这对于需要从中断点恢复训练的场景非常重要。
    """
    # 28. 创建模型和优化器
    model = StateDictModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    
    # 29. 假设已经训练了10个epoch
    epoch = 10
    best_loss = 0.25
    
    # 30. 构建检查点字典
    checkpoint = {
        'epoch': epoch,                 # 31. 当前的训练轮数
        'model_state_dict': model.state_dict(),  # 32. 模型参数
        'optimizer_state_dict': optimizer.state_dict(),  # 33. 优化器状态
        'scheduler_state_dict': scheduler.state_dict(),  # 34. 学习率调度器状态
        'best_loss': best_loss,         # 35. 最佳损失值
    }
    
    # 36. 保存检查点
    torch.save(checkpoint, 'training_checkpoint.pth')
    print(f"✅ 检查点已保存（epoch={epoch}, loss={best_loss}）")
    
    return checkpoint

def load_checkpoint():
    """37. 演示加载检查点
    
    加载检查点可以恢复训练状态，包括模型参数、优化器状态等。
    """
    # 38. 重新创建模型和优化器（结构要与保存时一致）
    model = StateDictModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    
    # 39. 加载检查点
    checkpoint = torch.load('training_checkpoint.pth')
    
    # 40. 恢复各组件状态
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    
    # 41. 恢复训练状态
    epoch = checkpoint['epoch']
    best_loss = checkpoint['best_loss']
    
    print(f"✅ 检查点已加载（epoch={epoch}, loss={best_loss}）")
    print(f"学习率已恢复为: {optimizer.param_groups[0]['lr']}")
    
    return epoch, model, optimizer, scheduler

if __name__ == "__main__":
    # 42. 测试所有保存和加载函数
    # 保存和加载整个模型
    save_entire_model()
    load_entire_model()
    
    # 保存和加载state_dict
    model = save_model_state_dict()
    load_model_state_dict()
    
    # 保存和加载检查点
    checkpoint = save_checkpoint()
    load_checkpoint()
