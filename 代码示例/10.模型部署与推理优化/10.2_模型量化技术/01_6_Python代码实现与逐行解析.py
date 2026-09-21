import torch                        # 1. 导入PyTorch核心库
import torch.nn as nn               # 2. 导入神经网络模块
import time                         # 3. 导入时间模块，用于性能测试
import os                           # 4. 导入操作系统模块，用于文件操作

# 5. 重新定义SimpleModel类（如果前面没有定义）
class SimpleModel(nn.Module):
    """6. 示例模型：用于演示量化"""
    
    def __init__(self, input_size=784, hidden_size=256, num_classes=10):
        """7. 模型初始化
        
        参数:
            input_size: 输入特征维度，默认784（28x28图像）
            hidden_size: 隐藏层维度，默认256
            num_classes: 输出类别数，默认10
        """
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)  # 8. 第一层全连接
        self.relu = nn.ReLU()                          # 9. 激活函数
        self.fc2 = nn.Linear(hidden_size, num_classes)  # 10. 输出层
    
    def forward(self, x):
        """11. 前向传播"""
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

def dynamic_quantization_example():
    """12. 动态量化示例
    
    动态量化在推理时将权重转为INT8，激活值动态量化。
    适用于LSTM、Transformer等模型。
    优点：实现简单，无需校准数据
    缺点：激活值每次都需要动态转换
    """
    # 13. 创建示例模型
    # 使用较大的输入维度模拟实际场景
    model = SimpleModel(input_size=784, hidden_size=256, num_classes=10)
    model.eval()                     # 14. 设置为评估模式
    
    # 15. 计算并打印原始模型大小
    def print_model_size(model, label="原始模型"):
        """16. 计算并打印模型大小
        
        参数:
            model: 要计算大小的模型
            label: 打印标签
        返回:
            size: 模型大小（MB）
        """
        # 17. 保存模型状态字典到临时文件
        torch.save(model.state_dict(), "temp_model.pt")
        
        # 18. 获取文件大小并转换为MB
        size = os.path.getsize("temp_model.pt") / (1024 * 1024)
        print(f"{label}大小: {size:.2f} MB")
        
        # 19. 清理临时文件
        os.remove("temp_model.pt")
        return size
    
    # 20. 计算原始FP32模型大小
    original_size = print_model_size(model, "原始FP32模型")
    
    # 21. 应用动态量化
    # quantize_dynamic函数将指定的层类型转换为量化版本
    # 参数：
    #   - model: 要量化的模型
    #   - {nn.Linear}: 要量化的层类型，这里只量化Linear层
    #   - dtype: 量化目标类型，torch.qint8表示8位有符号整数
    quantized_model = torch.quantization.quantize_dynamic(
        model,                              # 22. 要量化的模型
        {nn.Linear},                        # 23. 要量化的层类型（nn.Linear）
        dtype=torch.qint8                   # 24. 量化目标类型（8位整数）
    )
    
    # 25. 计算量化后模型大小
    quantized_size = print_model_size(quantized_model, "INT8量化模型")
    
    # 26. 计算并打印压缩比
    compression_ratio = original_size / quantized_size
    print(f"\n压缩比: {compression_ratio:.2f}x")
    
    # 27. 准备测试数据
    # 生成100个样本用于测试
    test_input = torch.randn(100, 784)
    
    # 28. 测试原始FP32模型推理速度
    model.eval()
    with torch.no_grad():
        start = time.time()         # 29. 记录开始时间
        for _ in range(100):        # 30. 运行100次推理
            _ = model(test_input)
        fp32_time = time.time() - start  # 31. 计算耗时
    
    # 32. 测试量化INT8模型推理速度
    quantized_model.eval()
    with torch.no_grad():
        start = time.time()
        for _ in range(100):
            _ = quantized_model(test_input)
        int8_time = time.time() - start
    
    # 33. 打印速度对比结果
    print(f"\n推理速度对比:")
    print(f"FP32模型: {fp32_time:.3f}s (100次推理)")
    print(f"INT8模型: {int8_time:.3f}s (100次推理)")
    print(f"速度提升: {fp32_time/int8_time:.2f}x")
    
    return quantized_model

if __name__ == "__main__":
    # 34. 执行动态量化示例
    quantized_model = dynamic_quantization_example()
    
    # 35. 验证量化模型可以正常推理
    test_input = torch.randn(1, 784)
    with torch.no_grad():
        output = quantized_model(test_input)
    print(f"\n量化模型输出形状: {output.shape}")
