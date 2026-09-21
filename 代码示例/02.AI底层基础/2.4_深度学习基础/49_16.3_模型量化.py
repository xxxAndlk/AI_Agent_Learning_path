def model_quantization():
    """模型量化"""
    
    model = SimpleModel()
    model.eval()
    
    # ===== 动态量化（Dynamic Quantization）=====
    # 最简单，在推理时动态转换为INT8
    # 权重转为INT8，激活保持FP32
    # 适用于LSTM、GRU等RNN模型
    
    # 动态量化
    quantized_model = torch.quantization.quantize_dynamic(
        model,
        {nn.Linear, nn.LSTM},  # 要量化的层类型
        dtype=torch.qint8      # 目标精度
    )
    
    # 保存量化模型
    torch.save(quantized_model.state_dict(), 'model_dynamic_quantized.pt')
    
    # 推理
    x = torch.randn(1, 3, 32, 32)
    output = quantized_model(x)
    print(f"动态量化后输出形状: {output.shape}")
    
    # ===== 静态量化（Static Quantization）=====
    # 需要校准数据集来确定激活范围
    # 适用于CNN等模型
    
    # 准备量化模型
    model_to_quantize = SimpleModel()
    model_to_quantize.eval()
    
    # 指定量化配置
    model_to_quantize.qconfig = torch.quantization.get_default_qconfig('fbgemm')
    
    # 准备层（融合卷积+BN+ReLU）
    torch.quantization.prepare(model_to_quantize, inplace=True)
    
    # 校准（使用代表性数据集）
    calibration_data = [torch.randn(10, 3, 32, 32) for _ in range(10)]
    with torch.no_grad():
        for data in calibration_data:
            model_to_quantize(data)
    
    # 转换为量化模型
    quantized_model_static = torch.quantization.convert(model_to_quantize, inplace=True)
    
    # 推理
    output = quantized_model_static(x)
    print(f"静态量化后输出形状: {output.shape}")
    
    # ===== 后训练量化（Post-Training Quantization, PTQ）=====
    # 使用torch.quantization.quantize_per_tensor
    
    def quantize_per_tensor_example():
        """逐张量量化"""
        
        # 原始FP32张量
        x = torch.randn(5, 5)
        
        # 动态量化（推理时自动确定范围）
        x_quantized = torch.quantize_per_tensor(
            x, 
            scale=0.1,      # 缩放因子
            zero_point=0,  # 零点
            dtype=torch.qint8
        )
        
        # 解量化回FP32
        x_dequantized = x_quantized.dequantize()
        
        print(f"原始类型: {x.dtype}")
        print(f"量化类型: {x_quantized.dtype}")
        print(f"解量化和原始的差异: {torch.max(torch.abs(x - x_dequantized))}")
    
    quantize_per_tensor_example()
    
    # ===== 量化感知训练（Quantization-Aware Training, QAT）=====
    # 在训练过程中模拟量化效果，精度更高
    # 适用于对精度要求高的场景
    
    class QuantizationAwareModel(nn.Module):
        """量化感知训练的模型"""
        def __init__(self):
            super().__init__()
            self.conv = nn.Conv2d(3, 64, 3, padding=1)
            self.bn = nn.BatchNorm2d(64)
            self.relu = nn.ReLU()
            self.fc = nn.Linear(64, 10)
        
        def forward(self, x):
            x = self.conv(x)
            x = self.bn(x)
            x = self.relu(x)
            x = x.mean(dim=[2, 3])
            return self.fc(x)
    
    # QAT流程
    # 1. 在模型中插入伪量化节点
    # 2. 正常训练
    # 3. 转换为量化模型
    
    return quantized_model
