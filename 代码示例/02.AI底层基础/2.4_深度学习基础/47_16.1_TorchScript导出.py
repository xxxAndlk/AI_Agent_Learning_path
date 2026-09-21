import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    """示例模型"""
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 64, 3, padding=1)
        self.bn = nn.BatchNorm2d(64)
        self.relu = nn.ReLU()
        self.fc = nn.Linear(64, 10)
    
    def forward(self, x):
        x = self.relu(self.bn(self.conv(x)))
        x = x.mean(dim=[2, 3])  # 全局平均池化
        return self.fc(x)


def torchscript_export():
    """TorchScript导出方法"""
    
    model = SimpleModel()
    model.eval()
    
    # 方法1：torch.jit.trace（跟踪执行）
    # 适用于不包含控制流的模型
    
    # 创建示例输入
    example_input = torch.randn(1, 3, 32, 32)
    
    # traced model
    traced_model = torch.jit.trace(model, example_input)
    
    # 保存
    traced_model.save('model_traced.pt')
    
    # 加载
    loaded_model = torch.jit.load('model_traced.pt')
    
    # 推理
    output = loaded_model(example_input)
    print(f"Traced模型输出形状: {output.shape}")
    
    # 方法2：torch.jit.script（脚本化）
    # 适用于包含控制流的模型
    
    @torch.jit.script
    def scripted_function(x):
        # JIT脚本函数
        if x.sum() > 0:
            return x * 2
        else:
            return x
    
    # 可以将整个模型进行script
    # scripted_model = torch.jit.script(model)
    
    # 方法3：torch.nn.Module的save/load（不推荐用于部署）
    # torch.save(model.state_dict(), 'model.pt')
    
    # 方法4：保存整个模型结构+参数
    # torch.save(model, 'full_model.pt')  # 不推荐
    
    return traced_model
