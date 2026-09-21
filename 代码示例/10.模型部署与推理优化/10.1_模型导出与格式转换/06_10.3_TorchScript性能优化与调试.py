import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块

class OptimizableModel(nn.Module):
    """3. 可优化的模型示例"""
    
    def __init__(self):
        """4. 模型初始化"""
        super(OptimizableModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(256 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 10)
    
    def forward(self, x):
        """5. 前向传播"""
        # 6. 特征提取
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        
        # 7. 展平
        x = x.view(x.size(0), -1)
        
        # 8. 分类
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def optimize_torchscript():
    """9. TorchScript模型性能优化技巧"""
    
    # 10. 创建并导出模型
    model = OptimizableModel()
    model.eval()
    
    example_input = torch.randn(1, 3, 32, 32)
    
    # 11. 基础Tracing
    traced = torch.jit.trace(model, example_input)
    
    # 12. 使用torch.jit.optimize_for_inference进行优化
    # 这个函数会应用一系列优化：
    # - 融合卷积和批量归一化
    # - 融合线性层
    # - 优化内存分配
    # - 启用推理优化
    optimized_model = torch.jit.optimize_for_inference(traced)
    
    # 13. 保存优化后的模型
    optimized_model.save('optimized_model.pt')
    print("✅ 优化后的模型已保存")
    
    # 14. 性能对比
    import time
    
    # 15. 预热（让CUDA等初始化完成）
    for _ in range(10):
        _ = traced(example_input)
        _ = optimized_model(example_input)
    
    # 16. 测试原始模型性能
    iterations = 100
    start = time.time()
    for _ in range(iterations):
        _ = traced(example_input)
    traced_time = time.time() - start
    
    # 17. 测试优化模型性能
    start = time.time()
    for _ in range(iterations):
        _ = optimized_model(example_input)
    optimized_time = time.time() - start
    
    print(f"原始模型耗时: {traced_time:.4f}秒")
    print(f"优化模型耗时: {optimized_time:.4f}秒")
    print(f"性能提升: {traced_time / optimized_time:.2f}x")
    
    return optimized_model

def frozen_optimization():
    """18. 使用freeze进一步优化模型
    
    freeze()会内联参数，使得模型完全自包含。
    这对于部署到没有PyTorch的环境特别有用。
    """
    # 19. 创建模型
    model = OptimizableModel()
    model.eval()
    
    # 20. 先Tracing
    traced = torch.jit.trace(model, torch.randn(1, 3, 32, 32))
    
    # 21. 使用freeze()冻结模型
    # freeze会：
    # - 将参数内联到计算图中
    # - 移除module层次结构
    # - 生成更紧凑的模型
    frozen_model = traced.freeze()
    
    # 22. 可以进一步优化
    optimized_frozen = torch.jit.optimize_for_inference(frozen_model)
    
    # 23. 保存
    optimized_frozen.save('frozen_optimized_model.pt')
    print("✅ 冻结优化模型已保存")
    
    return optimized_frozen

def script_optimization():
    """24. 使用Scripting方式并进行优化"""
    
    # 25. 定义模型
    model = OptimizableModel()
    model.eval()
    
    # 26. 使用Scripting
    scripted = torch.jit.script(model)
    
    # 27. 应用优化通道
    # 可以使用torch.jit.Sequential将多个优化串联
    from torch.jit._recursive import wrap_cpp_module
    
    # 28. 执行优化
    optimized = torch.jit.optimize_for_inference(scripted)
    
    # 29. 冻结
    frozen = optimized.freeze()
    
    frozen.save('script_optimized_model.pt')
    print("✅ Script优化模型已保存")
    
    return frozen

if __name__ == "__main__":
    # 30. 测试性能优化
    optimize_torchscript()
    frozen_optimization()
    script_optimization()
