import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块
from typing import Tuple, List  # 3. 导入类型提示

class ScriptingModel(nn.Module):
    """4. 支持Scripting导出的模型类
    
    注意：Scripting方式要求模型代码是TorchScript兼容的子集。
    一些Python特性如列表推导式、异常处理等可能不被支持。
    """
    
    def __init__(self, input_dim=128, hidden_dim=256, num_layers=3):
        """5. 模型初始化
        
        参数:
            input_dim: 输入特征维度
            hidden_dim: 隐藏层维度
            num_layers: 网络层数
        """
        super(ScriptingModel, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # 6. 动态创建多层网络
        layers = []
        for i in range(num_layers):
            if i == 0:
                layers.append(nn.Linear(input_dim, hidden_dim))
            else:
                layers.append(nn.Linear(hidden_dim, hidden_dim))
        
        # 7. 将层列表转换为ModuleList
        self.layers = nn.ModuleList(layers)
        self.output_layer = nn.Linear(hidden_dim, 10)
    
    def forward(self, x):
        """8. 前向传播方法
        
        参数:
            x: 输入张量
        返回:
            输出张量
        """
        # 9. 遍历每一层（Scripting支持for循环）
        for i, layer in enumerate(self.layers):
            x = layer(x)
            # 10. 应用ReLU激活函数（除了最后一层）
            if i < self.num_layers - 1:
                x = torch.relu(x)
        
        x = self.output_layer(x)
        return x

def export_with_scripting():
    """11. 使用TorchScript Scripting方式导出模型
    
    Scripting工作原理：
    1. 分析模型的代码，转换为TorchScript IR（中间表示）
    2. 生成完整的计算图，包括控制流
    
    优点：
    - 支持完整的Python控制流（if/else, for循环等）
    - 可以导出更复杂的模型结构
    - 生成的模型是完全可序列化的
    
    缺点：
    - 需要模型代码是TorchScript兼容的
    - 某些Python特性不被支持
    - 调试相对困难
    """
    # 12. 创建模型实例
    model = ScriptingModel()
    model.eval()
    
    # 13. 使用torch.jit.script进行脚本化导出
    # script会分析模型的代码结构，生成TorchScript程序
    scripted_model = torch.jit.script(model)
    
    # 14. 保存导出的模型
    scripted_model.save('scripted_model.pt')
    print("✅ Scripting模型已保存到 scripted_model.pt")
    
    # 15. 打印模型的图形表示
    print("\n=== Scripted Model Graph ===")
    print(scripted_model.graph)
    
    # 16. 打印模型的源代码表示
    print("\n=== Scripted Model Code ===")
    print(scripted_model.code)
    
    return scripted_model

def script_with_conditional():
    """17. 演示包含条件分支的模型导出
    
    对于包含if/else等控制流的模型，必须使用Scripting方式。
    Tracing方式只能记录实际执行到的路径。
    """
    # 18. 使用@torch.jit.script装饰器可以直接装饰forward方法
    # 但更常见的是直接使用torch.jit.script
    
    # 19. 定义一个简单的带条件分支的函数
    @torch.jit.script
    def conditional_function(x: torch.Tensor, use_relu: bool) -> torch.Tensor:
        """条件函数示例
        
        参数:
            x: 输入张量
            use_relu: 是否使用ReLU激活
        返回:
            输出张量
        """
        if use_relu:
            return torch.relu(x)
        else:
            return torch.tanh(x)
    
    # 20. 测试条件函数
    test_input = torch.randn(4, 8)
    output1 = conditional_function(test_input, True)
    output2 = conditional_function(test_input, False)
    
    print(f"使用ReLU: {output1.shape}")
    print(f"使用Tanh: {output2.shape}")
    
    return conditional_function

def script_with_loops():
    """21. 演示包含循环的模型导出
    
    对于需要迭代处理的模型，Scripting可以正确处理循环。
    """
    # 22. 定义一个包含循环的TorchScript函数
    @torch.jit.script
    def loop_processing(x: torch.Tensor, num_iterations: int) -> torch.Tensor:
        """循环处理示例
        
        参数:
            x: 输入张量
            num_iterations: 迭代次数
        返回:
            累积处理后的张量
        """
        # 23. 初始化输出
        result = x
        
        # 24. 循环处理（Scripting支持for循环）
        for i in range(num_iterations):
            # 每次迭代做一次非线性变换
            result = result * torch.sigmoid(result)
        
        return result
    
    # 25. 测试循环函数
    test_input = torch.randn(4, 8)
    output = loop_processing(test_input, 5)
    
    print(f"循环处理输出形状: {output.shape}")
    
    return loop_processing

def hybrid_tracing_scripting():
    """26. 混合使用Tracing和Scripting
    
    对于复杂的模型，可以分别对不同部分使用Tracing和Scripting，
    然后组合在一起。这种方式在实践中很常用。
    """
    # 27. 定义一个子模块，使用Scripting导出
    class SubModule(torch.nn.Module):
        def __init__(self):
            super(SubModule, self).__init__()
            self.fc = torch.nn.Linear(64, 64)
        
        def forward(self, x):
            # 28. 包含条件分支，需要使用Scripting
            if x.sum() > 0:
                return torch.relu(self.fc(x))
            else:
                return torch.tanh(self.fc(x))
    
    # 29. 将子模块Script化
    sub_module = torch.jit.script(SubModule())
    
    # 30. 定义主模块，使用Tracing
    class MainModule(torch.nn.Module):
        def __init__(self, submod):
            super(MainModule, self).__init__()
            self.submodule = submod  # 31. 嵌入Script化的子模块
            self.main_fc = torch.nn.Linear(128, 64)
        
        def forward(self, x):
            x = self.main_fc(x)
            x = self.submodule(x)  # 32. 调用Script化子模块
            return x
    
    # 33. 创建主模块并Tracing
    main_module = MainModule(sub_module)
    main_module.eval()
    
    example_input = torch.randn(4, 128)
    # 34. Tracing会自动包含已Script化的子模块
    traced_hybrid = torch.jit.trace(main_module, example_input)
    
    traced_hybrid.save('hybrid_model.pt')
    print("✅ 混合模型已保存")
    
    return traced_hybrid

if __name__ == "__main__":
    # 35. 测试所有Scripting功能
    export_with_scripting()
    script_with_conditional()
    script_with_loops()
    hybrid_tracing_scripting()
