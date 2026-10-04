import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块
import torch.onnx               # 3. 导入ONNX模块

class AdvancedModel(nn.Module):
    """4. 高级模型示例，包含多种操作"""
    
    def __init__(self):
        """5. 模型初始化"""
        super(AdvancedModel, self).__init__()
        self.conv = nn.Conv2d(3, 64, 3, padding=1)
        self.bn = nn.BatchNorm2d(64)
        self.linear = nn.Linear(64, 10)
    
    def forward(self, x):
        """6. 前向传播"""
        x = self.conv(x)
        x = self.bn(x)
        x = torch.relu(x)
        x = torch.mean(x, dim=[2, 3])  # 自适应平均池化
        x = self.linear(x)
        return x

def export_with_opset_version():
    """7. 演示不同opset版本的选择
    
    ONNX算子集（opset）版本影响支持的算子和功能。
    常用版本：
    - opset 9/11: 早期版本，仅兼容旧运行时时使用
    - opset 13/14/15: 旧稳定版本，兼容性好
    - opset 17/18: PyTorch 2.x默认导出版本，推荐使用
    - opset 21+: 较新版本，支持更多新算子
    
    选择建议：
    - 目标运行时支持最新版本就用最新的
    - 如果遇到兼容性问题，尝试降低版本
    """
    # 8. 创建模型
    model = AdvancedModel()
    model.eval()
    
    example_input = torch.randn(1, 3, 32, 32)
    
    # 9. 尝试不同opset版本
    for opset_version in [11, 13, 17, 18]:
        try:
            torch.onnx.export(
                model,
                example_input,
                f'model_opset{opset_version}.onnx',
                export_params=True,
                opset_version=opset_version,
                input_names=['input'],
                output_names=['output']
            )
            print(f"✅ opset{opset_version} 导出成功")
        except Exception as e:
            print(f"❌ opset{opset_version} 导出失败: {e}")

def export_with_custom_ops():
    """10. 处理自定义算子的导出
    
    如果模型包含ONNX不支持的算子，可以：
    1. 重新实现该算子
    2. 使用符号函数（symbolic）映射到ONNX支持的算子
    3. 跳过该算子（在导出后处理）
    """
    # 11. 定义一个包含自定义操作的模型
    class CustomOpModel(nn.Module):
        def __init__(self):
            super(CustomOpModel, self).__init__()
            self.conv = nn.Conv2d(3, 32, 3, padding=1)
        
        def forward(self, x):
            """12. 前向传播，包含自定义操作
            
            假设custom_function是一个不ONNX兼容的函数
            """
            x = self.conv(x)
            
            # 13. 使用PyTorch内置操作替代自定义操作
            # 在导出前，将自定义操作替换为ONNX支持的等效操作
            # 例如：如果有自定义的smooth操作，可以用以下方式替代
            # x = custom_smooth(x)  # 原始的自定义操作
            x = torch.nn.functional.avg_pool2d(x, kernel_size=3, stride=1, padding=1)
            
            return x
    
    # 14. 导出
    model = CustomOpModel()
    model.eval()
    
    torch.onnx.export(
        model,
        torch.randn(1, 3, 32, 32),
        'custom_op_model.onnx',
        export_params=True,
        opset_version=13,
        input_names=['input'],
        output_names=['output']
    )
    print("✅ 自定义算子模型已导出")

def export_with_symbolic_functions():
    """15. 使用符号函数处理复杂操作
    
    某些PyTorch操作在ONNX中没有直接对应，可以通过注册符号函数来处理。
    这需要较深的ONNX知识，适合高级用户。
    """
    # 16. 定义需要特殊处理的模型
    class ComplexOpModel(nn.Module):
        def __init__(self):
            super(ComplexOpModel, self).__init__()
            self.pool = nn.AdaptiveAvgPool2d((1, 1))
        
        def forward(self, x):
            # 17. AdaptiveAvgPool2d在ONNX中有对应算子
            x = self.pool(x)
            return x
    
    # 18. 某些操作可能需要自定义符号函数
    # 这里展示一个更通用的方法
    # 注意：实际项目中应该避免使用不支持的操作
    
    model = ComplexOpModel()
    model.eval()
    
    torch.onnx.export(
        model,
        torch.randn(1, 3, 32, 32),
        'complex_op_model.onnx',
        export_params=True,
        opset_version=13,
        input_names=['input'],
        output_names=['output']
    )
    print("✅ 复杂操作模型已导出")

def handle_export_errors():
    """19. 处理ONNX导出常见错误
    
    常见错误及解决方案：
    1. Unsupported ops: 使用支持的操作替代
    2. Dynamic control flow: 使用Scripting或重新设计模型
    3. Type mismatch: 确保输入类型正确
    4. Shape inference failed: 提供正确的示例输入
    """
    # 20. 模拟一个可能失败的模型
    class ProblematicModel(nn.Module):
        def __init__(self):
            super(ProblematicModel, self).__init__()
        
        def forward(self, x):
            # 21. 动态控制流问题
            # if语句在导出时可能出现问题
            if x.sum() > 0:
                return torch.relu(x)
            else:
                return torch.tanh(x)
    
    # 22. 解决方案：使用torch.cond或重新设计模型
    class FixedModel(nn.Module):
        def __init__(self):
            super(FixedModel, self).__init__()
        
        def forward(self, x):
            # 23. 使用确定性操作替代条件分支
            # 或者将条件移到模型外部
            mask = (x.sum(dim=[1, 2, 3], keepdim=True) > 0).float()
            return mask * torch.relu(x) + (1 - mask) * torch.tanh(x)
    
    # 24. 导出修复后的模型
    model = FixedModel()
    model.eval()
    
    try:
        torch.onnx.export(
            model,
            torch.randn(1, 3, 32, 32),
            'fixed_model.onnx',
            export_params=True,
            opset_version=13
        )
        print("✅ 修复后的模型导出成功")
    except Exception as e:
        print(f"❌ 导出失败: {e}")

if __name__ == "__main__":
    # 25. 测试高级导出功能
    export_with_opset_version()
    export_with_custom_ops()
    handle_export_errors()
