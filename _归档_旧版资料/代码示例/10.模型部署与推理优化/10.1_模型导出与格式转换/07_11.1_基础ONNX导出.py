import numpy as np
import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块
import torch.onnx               # 3. 导入ONNX模块

class ONNXExportableModel(nn.Module):
    """4. 准备导出到ONNX的模型类
    
    并非所有PyTorch模型都可以直接导出到ONNX。
    模型需要满足以下条件：
    1. 所有操作都有ONNX算子对应实现
    2. 不包含动态控制流（if/else, for循环等）
    3. 张量类型和形状在导出时确定
    """
    
    def __init__(self, in_channels=3, num_classes=10):
        """5. 模型初始化
        
        参数:
            in_channels: 输入通道数，RGB图像为3
            num_classes: 分类类别数
        """
        super(ONNXExportableModel, self).__init__()
        
        # 6. 特征提取部分：三个卷积块
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        # 7. 分类器部分
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        """8. 前向传播方法
        
        参数:
            x: 输入张量，形状为(batch_size, in_channels, height, width)
        返回:
            output: 分类 logits，形状为(batch_size, num_classes)
        """
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.classifier(x)
        return x

def basic_onnx_export():
    """9. 基础ONNX导出示例
    
    torch.onnx.export的常用参数：
    - model: 要导出的PyTorch模型
    - args: 示例输入，用于确定模型输入形状
    - f: 输出文件路径
    - export_params: 是否导出参数权重
    - opset_version: ONNX算子集版本
    - do_constant_folding: 是否进行常量折叠
    - input_names: 输入张量名称列表
    - output_names: 输出张量名称列表
    - dynamic_axes: 动态维度配置
    """
    # 10. 创建模型实例
    model = ONNXExportableModel(in_channels=3, num_classes=10)
    model.eval()                # 11. 必须设置为评估模式
    
    # 12. 创建示例输入
    # ONNX导出需要确定输入形状，示例输入的形状应该与实际输入一致
    example_input = torch.randn(1, 3, 32, 32)
    
    # 13. 执行ONNX导出
    torch.onnx.export(
        model,                      # 14. 要导出的模型
        example_input,              # 15. 示例输入
        'basic_model.onnx',         # 16. 输出文件路径
        export_params=True,         # 17. 导出模型权重参数
        opset_version=13,           # 18. ONNX算子集版本（推荐13或更高）
        do_constant_folding=True,   # 19. 常量折叠优化，减少图节点
        input_names=['input'],      # 20. 输入张量名称（用于调试和推理）
        output_names=['output'],    # 21. 输出张量名称
        dynamic_axes={              # 22. 动态轴配置
            'input': {0: 'batch_size', 2: 'height', 3: 'width'},
            'output': {0: 'batch_size'}
        }
    )
    
    print("✅ 基础ONNX模型已导出到 basic_model.onnx")

def onnx_export_with_dynamic_shapes():
    """23. 支持动态输入形状的ONNX导出
    
    通过dynamic_axes参数，可以指定哪些维度是动态的。
    这对于需要处理不同batch size或图像尺寸的场景非常有用。
    """
    # 24. 创建模型
    model = ONNXExportableModel(in_channels=3, num_classes=10)
    model.eval()
    
    # 25. 动态轴配置详解
    # key: 张量名称（必须与input_names/output_names中的名称一致）
    # value: 字典，键是维度索引，值是维度名称
    # 维度名称是用于调试的标识符，不是实际维度值
    dynamic_axes = {
        'input': {
            0: 'batch_size',        # 26. 批次大小维度是动态的
            2: 'height',            # 27. 图像高度是动态的
            3: 'width'              # 28. 图像宽度是动态的
        },
        'output': {
            0: 'batch_size'         # 29. 输出批次大小也是动态的
        }
    }
    
    # 30. 示例输入使用固定形状
    # 但dynamic_axes会让ONNX模型接受不同形状的输入
    example_input = torch.randn(1, 3, 32, 32)
    
    torch.onnx.export(
        model,
        example_input,
        'dynamic_model.onnx',
        export_params=True,
        opset_version=13,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes=dynamic_axes
    )
    
    print("✅ 动态形状ONNX模型已导出到 dynamic_model.onnx")

def onnx_export_with_multiple_inputs():
    """31. 多输入多输出模型的ONNX导出
    
    某些模型有多个输入或输出，例如：
    - 图像分割模型：输入图像 + 图像掩码
    - 文本模型：input_ids + attention_mask
    - 多任务学习模型：多个输出头
    """
    # 32. 定义多输入输出模型
    class MultiIONet(nn.Module):
        def __init__(self):
            super(MultiIONet, self).__init__()
            self.image_encoder = nn.Sequential(
                nn.Conv2d(3, 32, 3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1))
            )
            self.text_encoder = nn.Sequential(
                nn.Linear(768, 128),
                nn.ReLU()
            )
            self.fusion = nn.Sequential(
                nn.Linear(32 + 128, 64),
                nn.ReLU(),
                nn.Linear(64, 10)
            )
        
        def forward(self, image_input, text_input):
            """33. 前向传播方法
            
            参数:
                image_input: 图像输入，形状为(batch, 3, 224, 224)
                text_input: 文本特征输入，形状为(batch, 768)
            返回:
                output: 分类 logits
            """
            # 34. 编码图像
            image_feat = self.image_encoder(image_input)
            image_feat = image_feat.view(image_feat.size(0), -1)
            
            # 35. 编码文本
            text_feat = self.text_encoder(text_input)
            
            # 36. 特征融合
            combined = torch.cat([image_feat, text_feat], dim=1)
            output = self.fusion(combined)
            
            return output
    
    # 37. 创建模型
    model = MultiIONet()
    model.eval()
    
    # 38. 准备多个示例输入
    example_image = torch.randn(2, 3, 224, 224)
    example_text = torch.randn(2, 768)
    
    # 39. 导出时需要用tuple提供多个输入
    torch.onnx.export(
        model,
        (example_image, example_text),  # 40. 元组形式提供多输入
        'multi_io_model.onnx',
        export_params=True,
        opset_version=13,
        input_names=['image_input', 'text_input'],  # 41. 多个输入名称
        output_names=['output'],
        dynamic_axes={
            'image_input': {0: 'batch_size'},
            'text_input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print("✅ 多输入输出ONNX模型已导出")

def onnx_export_verification():
    """42. 验证ONNX模型
    
    导出后应该验证模型的正确性，确保输出与PyTorch模型一致。
    可以使用ONNX库的推理功能进行验证。
    """
    try:
        import onnx
    except ImportError:
        print("请安装ONNX: pip install onnx")
        return
    
    # 43. 加载ONNX模型
    onnx_model = onnx.load('basic_model.onnx')
    
    # 44. 检查模型结构是否有效
    onnx.checker.check_model(onnx_model)
    print("✅ ONNX模型结构验证通过")
    
    # 45. 打印模型信息
    print(f"\n=== ONNX模型信息 ===")
    print(f"图输入: {[inp.name for inp in onnx_model.graph.input]}")
    print(f"图输出: {[out.name for out in onnx_model.graph.output]}")
    print(f"节点数量: {len(onnx_model.graph.node)}")
    
    # 46. 使用ONNX Runtime进行推理验证
    try:
        import onnxruntime as ort
        
        # 47. 创建推理会话
        session = ort.InferenceSession('basic_model.onnx')
        
        # 48. 准备输入数据
        test_input = torch.randn(1, 3, 32, 32).numpy()
        
        # 49. 运行推理
        onnx_output = session.run(None, {'input': test_input})[0]
        
        # 50. 与PyTorch模型输出对比
        pytorch_model = ONNXExportableModel(in_channels=3, num_classes=10)
        pytorch_model.eval()
        
        with torch.no_grad():
            pytorch_output = pytorch_model(torch.from_numpy(test_input)).numpy()
        
        # 51. 计算差异
        diff = numpy.abs(onnx_output - pytorch_output)
        max_diff = diff.max()
        mean_diff = diff.mean()
        
        print(f"\n=== 输出对比 ===")
        print(f"最大差异: {max_diff}")
        print(f"平均差异: {mean_diff}")
        
        if max_diff < 1e-5:
            print("✅ ONNX模型输出与PyTorch模型一致")
        else:
            print("⚠️ 输出存在差异，可能影响应用")
            
    except ImportError:
        print("请安装ONNX Runtime: pip install onnxruntime")

if __name__ == "__main__":
    # 52. 测试ONNX导出功能
    basic_onnx_export()
    onnx_export_with_dynamic_shapes()
    onnx_export_with_multiple_inputs()
    onnx_export_verification()
