import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块
import torch.nn.functional as F  # 3. 导入函数式API

class TracingModel(nn.Module):
    """4. 示例模型类，用于演示TorchScript Tracing导出"""
    
    def __init__(self, input_dim=128, hidden_dim=256, num_classes=10):
        """5. 模型初始化
        
        参数:
            input_dim: 输入特征维度
            hidden_dim: 隐藏层维度
            num_classes: 输出类别数
        """
        super(TracingModel, self).__init__()
        # 6. 定义模型层
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, num_classes)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        """7. 前向传播方法
        
        参数:
            x: 输入张量，形状为(batch_size, input_dim)
        返回:
            output: 输出张量，形状为(batch_size, num_classes)
        """
        # 8. 简单的三层全连接网络
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

def export_with_tracing():
    """9. 使用TorchScript Tracing方式导出模型
    
    Tracing工作原理：
    1. 使用示例输入执行模型
    2. 记录前向传播过程中的所有操作
    3. 生成一个静态计算图
    
    优点：
    - 使用简单，只需提供示例输入
    - 不需要修改现有模型代码
    - 支持大部分PyTorch操作
    
    缺点：
    - 不支持动态控制流（if/else, for循环等）
    - 只会记录实际执行到的路径
    - 对于有条件分支的模型，可能丢失某些分支
    """
    # 10. 创建模型实例
    model = TracingModel()
    model.eval()                # 11. 必须设置为评估模式
    
    # 12. 创建示例输入
    # 示例输入的形状和类型必须与实际输入一致
    example_input = torch.randn(8, 128)  # batch_size=8, input_dim=128
    
    # 13. 使用torch.jit.trace进行追踪导出
    # 第一个参数是模型，第二个参数是示例输入
    # trace会执行一次前向传播，记录所有操作
    traced_model = torch.jit.trace(model, example_input)
    
    # 14. 保存导出的模型
    # 可以使用.pt或.pth作为文件扩展名
    traced_model.save('traced_model.pt')
    print("✅ Tracing模型已保存到 traced_model.pt")
    
    # 15. 打印模型的图形表示（用于调试）
    print("\n=== Traced Model Graph ===")
    print(traced_model.graph)
    
    # 16. 打印模型的源代码表示
    print("\n=== Traced Model Code ===")
    print(traced_model.code)
    
    return traced_model

def verify_traced_model():
    """17. 验证导出的Tracing模型"""
    # 18. 加载Tracing模型
    loaded_model = torch.jit.load('traced_model.pt')
    loaded_model.eval()
    
    # 19. 创建测试输入
    test_input = torch.randn(16, 128)
    
    # 20. 分别使用原模型和Tracing模型进行推理
    original_model = TracingModel()
    original_model.eval()
    
    with torch.no_grad():
        # 21. 原模型推理
        original_output = original_model(test_input)
        # 22. Tracing模型推理
        traced_output = loaded_model(test_input)
    
    # 23. 比较输出是否一致
    is_close = torch.allclose(original_output, traced_output, rtol=1e-5, atol=1e-7)
    print(f"输出是否一致: {is_close}")
    
    if not is_close:
        # 24. 计算差异
        diff = torch.abs(original_output - traced_output)
        print(f"最大差异: {diff.max().item()}")
        print(f"平均差异: {diff.mean().item()}")
    
    return is_close

def advanced_tracing_with_constraints():
    """25. 使用约束进行高级Tracing
    
    torch.jit.trace接受一个strict参数（默认True）。
    当strict=False时，允许 Tracing 在遇到某些不支持的操作时继续进行。
    这对于包含一些Tracing不支持操作的模型很有用。
    """
    # 26. 创建模型
    model = TracingModel()
    model.eval()
    
    # 27. 示例输入
    example_input = torch.randn(4, 128)
    
    # 28. 使用strict=False进行追踪
    # 当模型包含Tracing不完全支持的操作时，使用此选项
    try:
        traced_model = torch.jit.trace(model, example_input, strict=True)
        print("✅ 严格模式追踪成功")
    except Exception as e:
        print(f"严格模式失败: {e}")
        # 29. 尝试非严格模式
        traced_model = torch.jit.trace(model, example_input, strict=False)
        print("✅ 非严格模式追踪成功")
    
    return traced_model
