import torch                        # 1. 导入PyTorch核心库，提供深度学习模型创建和操作功能
import torch.nn as nn               # 2. 导入神经网络模块，包含各种层和激活函数定义

class SimpleModel(nn.Module):
    """3. 示例模型：用于演示模型导出流程"""
    
    def __init__(self, input_size=10, hidden_size=64, num_classes=3):
        """4. 模型初始化方法
        
        参数:
            input_size: 输入特征维度，默认10
            hidden_size: 隐藏层维度，默认64
            num_classes: 输出类别数，默认3
        """
        super().__init__()          # 5. 调用父类构造函数，初始化nn.Module
        self.fc1 = nn.Linear(input_size, hidden_size)  # 6. 第一个全连接层
        self.relu = nn.ReLU()       # 7. ReLU激活函数
        self.dropout = nn.Dropout(0.2)  # 8. Dropout层，防止过拟合
        self.fc2 = nn.Linear(hidden_size, num_classes)  # 9. 输出层
    
    def forward(self, x):
        """10. 前向传播方法
        
        参数:
            x: 输入张量，形状为(batch_size, input_size)
        返回:
            输出张量，形状为(batch_size, num_classes)
        """
        x = self.fc1(x)             # 11. 第一个全连接层计算
        x = self.relu(x)            # 12. 激活函数
        x = self.dropout(x)          # 13. Dropout正则化
        x = self.fc2(x)             # 14. 输出层计算
        return x                     # 15. 返回分类结果

def export_to_torchscript(model, example_input, save_path="model.pt"):
    """16. 导出为TorchScript格式
    
    TorchScript允许模型脱离Python环境运行，适合生产部署。
    使用tracing方式，将模型执行过程记录为计算图。
    
    参数:
        model: 要导出的PyTorch模型
        example_input: 示例输入，用于tracing
        save_path: 保存路径
    返回:
        traced_model: 导出的TorchScript模型对象
    """
    # 17. 使用tracing方式导出
    # trace会记录模型在前向传播中的所有操作
    # example_input的形状必须与实际输入一致
    traced_model = torch.jit.trace(model, example_input)
    
    # 18. 保存模型为.pt文件
    # 保存的模型可以在后续使用torch.jit.load加载
    traced_model.save(save_path)
    print(f"✅ TorchScript模型已保存至: {save_path}")
    
    return traced_model

def export_to_onnx(model, example_input, save_path="model.onnx"):
    """19. 导出为ONNX格式
    
    ONNX是开放的神经网络交换格式，支持跨平台部署。
    导出的模型可以被ONNX运行时、TensorRT、ONNX.js等执行。
    
    参数:
        model: 要导出的PyTorch模型
        example_input: 示例输入
        save_path: 保存路径
    """
    # 20. 将模型设置为评估模式
    # 评估模式会禁用dropout等训练特定的层
    model.eval()
    
    # 21. 导出ONNX模型
    # torch.onnx.export是PyTorch内置的ONNX导出函数
    torch.onnx.export(
        model,                              # 22. 要导出的模型
        example_input,                      # 23. 示例输入，用于确定输入形状
        save_path,                          # 24. 保存路径
        export_params=True,                 # 25. 是否导出模型参数，True表示导出权重
        opset_version=17,                   # 26. ONNX算子集版本，17/18为PyTorch 2.x常用导出版本
        do_constant_folding=True,           # 27. 是否进行常量折叠优化
        input_names=['input'],              # 28. 输入张量的名称，便于后续引用
        output_names=['output'],            # 29. 输出张量的名称
        dynamic_axes={                      # 30. 动态维度配置，支持变长输入
            'input': {0: 'batch_size'},     # 31. 第一个维度是动态的，表示batch_size
            'output': {0: 'batch_size'}     # 32. 输出batch_size也可以变化
        }
    )
    print(f"✅ ONNX模型已保存至: {save_path}")

def load_and_inference_torchscript(model_path, input_data):
    """33. 加载TorchScript模型并进行推理
    
    TorchScript模型的优点是可以脱离原始模型类定义加载。
    
    参数:
        model_path: 模型文件路径
        input_data: 输入数据
    返回:
        output: 模型推理结果
    """
    # 34. 加载TorchScript模型
    # 不需要Python类定义，模型完全自包含
    model = torch.jit.load(model_path)
    model.eval()                     # 35. 设置为评估模式
    
    # 36. 推理时不计算梯度，节省内存和计算资源
    with torch.no_grad():
        output = model(input_data)  # 37. 执行前向传播
    
    return output

if __name__ == "__main__":
    # 38. 创建示例模型实例
    model = SimpleModel()
    model.eval()                     # 39. 设置为评估模式
    
    # 40. 创建示例输入张量
    # 形状(batch_size=1, input_size=10)
    example_input = torch.randn(1, 10)
    
    # 41. 导出为TorchScript格式
    export_to_torchscript(model, example_input, "simple_model.pt")
    
    # 42. 导出为ONNX格式
    export_to_onnx(model, example_input, "simple_model.onnx")
    
    # 43. 测试加载TorchScript模型
    # 使用批量输入(5个样本)进行测试
    test_input = torch.randn(5, 10)
    output = load_and_inference_torchscript("simple_model.pt", test_input)
    print(f"推理结果形状: {output.shape}")  # 44. 打印输出形状
