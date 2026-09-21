import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块
import numpy as np              # 3. 导入NumPy

class TensorRTCompatibleModel(nn.Module):
    """4. TensorRT兼容的模型示例
    
    为了获得最佳TensorRT性能，模型应该：
    1. 使用TensorRT支持的算子
    2. 避免动态形状（固定输入形状更快）
    3. 使用批量操作替代循环
    """
    
    def __init__(self):
        """5. 模型初始化"""
        super(TensorRTCompatibleModel, self).__init__()
        
        # 6. 使用卷积和池化（TensorRT高度优化）
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        self.pool = nn.MaxPool2d(2, 2)
        
        # 7. 全连接层
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, 10)
        
        # 8. Dropout在推理时会被忽略
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        """9. 前向传播方法
        
        参数:
            x: 输入张量，形状为(batch, 3, 32, 32)
        返回:
            output: 分类输出，形状为(batch, 10)
        """
        # 10. 三个卷积块
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool(torch.relu(self.bn3(self.conv3(x))))
        
        # 11. 展平
        x = x.view(x.size(0), -1)
        
        # 12. 全连接层
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        
        return x

def export_to_onnx_for_tensorrt():
    """13. 导出适合TensorRT的ONNX模型
    
    TensorRT优化要求：
    1. ONNX模型必须是稳定的，opset版本推荐17或更高（PyTorch 2.x默认18）
    2. 最好固定输入形状（dynamic_axes慎用）
    3. 避免使用TensorRT不支持的算子
    """
    # 14. 创建模型
    model = TensorRTCompatibleModel()
    model.eval()
    
    # 15. 准备固定形状的示例输入
    # 固定batch_size为1或更大的值可以获得更好性能
    example_input = torch.randn(1, 3, 32, 32)
    
    # 16. 导出ONNX
    torch.onnx.export(
        model,
        example_input,
        'tensorrt_model.onnx',
        export_params=True,
        opset_version=17,           # 17. 推荐使用17或更高版本（PyTorch 2.x默认18）
        do_constant_folding=True,   # 18. 常量折叠
        input_names=['input'],      # 19. 输入名称
        output_names=['output'],    # 20. 输出名称
        # 21. 动态轴：TensorRT对动态支持有限，谨慎使用
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print("✅ 适合TensorRT的ONNX模型已导出")
    return 'tensorrt_model.onnx'

def tensorrt_optimization():
    """22. TensorRT优化演示（需要安装tensorrt库）
    
    注意：此代码需要安装NVIDIA TensorRT库。
    在实际环境中，需要使用pycuda和tensorrt包。
    """
    try:
        import tensorrt as trt
        import pycuda.driver as cuda
    except ImportError:
        print("请安装TensorRT: 需要NVIDIA TensorRT和pycuda")
        print("pip install nvidia-tensorrt pycuda")
        return None
    
    # 23. 创建TensorRT logger
    # Logger用于记录优化过程中的信息
    logger = trt.Logger(trt.Logger.WARNING)
    
    # 24. 创建builder
    builder = trt.Builder(logger)
    
    # 25. 创建network
    # explicit_batch标志允许处理可变batch size
    # explicit_weight标志允许更灵活的权重格式
    network_flags = 1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    network = builder.create_network(network_flags)
    
    # 26. 创建ONNX parser
    parser = trt.OnnxParser(network, logger)
    
    # 27. 读取ONNX文件
    with open('tensorrt_model.onnx', 'rb') as f:
        onnx_model_data = f.read()
    
    # 28. 解析ONNX
    if not parser.parse(onnx_model_data):
        print("❌ ONNX解析失败")
        for error in range(parser.num_errors):
            print(f"错误 {error}: {parser.get_error(error)}")
        return None
    
    # 29. 配置builder
    # workspace_size: TensorRT使用的最大显存（字节）
    # 推荐设置为1-2GB
    builder.max_workspace_size = 1 << 30  # 1GB
    
    # 30. 配置精度
    # FP16: 半精度浮点数，速度快但精度略低
    if builder.platform_has_tf32:
        # TF32是A100等新GPU的特性
        print("支持TF32精度")
    
    if builder.platform_has_fp16:
        builder.fp16_mode = True
        print("启用FP16模式")
    
    # 31. INT8量化（需要校准数据集）
    # builder.int8_mode = True
    # builder.int8_calibrator = calibrator
    
    # 32. 构建engine
    print("⏳ 正在构建TensorRT引擎...")
    engine = builder.build_cuda_engine(network)
    
    if engine is None:
        print("❌ 引擎构建失败")
        return None
    
    # 33. 保存engine（避免重复构建）
    with open('tensorrt_engine.plan', 'wb') as f:
        engine.serialize()
        f.write(engine)
    
    print(f"✅ TensorRT引擎已构建")
    print(f"引擎信息:")
    print(f"  - 最大batch size: {engine.max_batch_size}")
    print(f"  - 输入数量: {engine.num_inputs}")
    print(f"  - 输出数量: {engine.num_outputs}")
    print(f"  - 层数: {engine.num_layers}")
    
    return engine

def tensorrt_inference():
    """34. TensorRT推理演示"""
    try:
        import tensorrt as trt
        import pycuda.driver as cuda
        import pycuda
    except ImportError:
        print("请安装TensorRT和pycuda")
        return
    
    # 35. 加载engine
    with open('tensorrt_engine.plan', 'rb') as f:
        engine_data = f.read()
    
    logger = trt.Logger(trt.Logger.WARNING)
    runtime = trt.Runtime(logger)
    engine = runtime.deserialize_cuda_engine(engine_data)
    
    # 36. 创建context
    context = engine.create_execution_context()
    
    # 37. 准备输入数据
    test_input = np.random.randn(1, 3, 32, 32).astype(np.float32)
    input_size = test_input.nbytes
    output_size = np.zeros((1, 10), dtype=np.float32).nbytes
    
    # 38. 分配GPU内存
    cuda.init()
    device = cuda.Device(0)
    context = device.make_context()
    
    d_input = cuda.mem_alloc(input_size)
    d_output = cuda.mem_alloc(output_size)
    
    # 39. 绑定流
    stream = cuda.Stream()
    
    # 40. 复制输入到GPU
    cuda.memcpy_htod_async(d_input, test_input, stream)
    
    # 41. 执行推理
    context.execute_async_v2(
        bindings=[int(d_input), int(d_output)],
        stream_handle=stream.handle
    )
    
    # 42. 复制输出到CPU
    output = np.empty((1, 10), dtype=np.float32)
    cuda.memcpy_dtoh_async(output, d_output, stream)
    stream.synchronize()
    
    print(f"TensorRT推理结果: {output.shape}")
    print(f"预测类别: {np.argmax(output)}")
    
    # 43. 清理
    del context
    del engine
    del runtime

def int8_quantization():
    """44. INT8量化演示
    
    INT8量化可以显著减少模型大小和加速推理，
    但可能带来一定的精度损失。
    
    量化流程：
    1. 准备校准数据集
    2. 运行校准，获取各层的数据分布
    3. 根据分布进行量化
    """
    print("INT8量化需要以下步骤：")
    print("1. 准备校准数据集（至少100-1000个样本）")
    print("2. 实现INT8 calibrator类")
    print("3. 配置builder使用INT8模式")
    print("4. 运行校准并构建engine")
    print("\n示例校准器实现：")
    print("""
class Int8Calibrator(trt.IInt8EntropyCalibrator2):
    def __init__(self, calibration_data):
        super().__init__()
        self.calibration_data = calibration_data
        self.batch_size = 32
        self.current_idx = 0
        
    def get_batch(self, names):
        if self.current_idx >= len(self.calibration_data):
            return None
        batch = self.calibration_data[self.current_idx:self.current_idx+self.batch_size]
        self.current_idx += self.batch_size
        return [int(cuda.mem_alloc(batch.nbytes))]
        
    def get_batch_size(self):
        return self.batch_size
    """)

if __name__ == "__main__":
    # 45. 测试TensorRT导出
    export_to_onnx_for_tensorrt()
    # tensorrt_optimization()  # 需要安装TensorRT
    # tensorrt_inference()     # 需要安装TensorRT
