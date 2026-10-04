import torch                    # 1. 导入PyTorch库
import torch.nn as nn           # 2. 导入神经网络模块
import numpy as np              # 3. 导入NumPy用于数据处理

class RuntimeTestModel(nn.Module):
    """4. 用于Runtime测试的模型"""
    
    def __init__(self):
        """5. 模型初始化"""
        super(RuntimeTestModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, 3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.fc = nn.Linear(256 * 4 * 4, 10)
    
    def forward(self, x):
        """6. 前向传播"""
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

def export_for_runtime():
    """7. 导出适合ONNX Runtime的模型"""
    # 8. 创建模型
    model = RuntimeTestModel()
    model.eval()
    
    # 9. 导出为ONNX
    torch.onnx.export(
        model,
        torch.randn(1, 3, 32, 32),
        'runtime_model.onnx',
        export_params=True,
        opset_version=13,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    print("✅ Runtime模型已导出")
    return 'runtime_model.onnx'

def basic_onnx_runtime_inference():
    """10. ONNX Runtime基础推理"""
    try:
        import onnxruntime as ort
    except ImportError:
        print("请安装ONNX Runtime: pip install onnxruntime")
        return
    
    # 11. 创建推理会话
    # 可以配置各种执行选项
    session_options = ort.SessionOptions()
    
    # 12. 启用图优化
    # graph_optimization_level有多个级别：
    # - ORT_DISABLE_ALL: 禁用所有优化
    # - ORT_ENABLE_BASIC: 启用基本优化
    # - ORT_ENABLE_EXTENDED: 启用扩展优化（推荐）
    # - ORT_ENABLE_ALL: 启用所有优化
    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
    
    # 13. 启用执行 provider
    # 可用的provider:
    # - CUDA: NVIDIA GPU加速
    # - CPU: CPU执行
    # - TensorRT: NVIDIA TensorRT加速
    # - CoreML: Apple设备加速
    # - DirectML: Windows GPU加速
    
    # 创建会话（尝试使用CUDA，如果不可用则回退到CPU）
    providers = []
    if 'CUDAExecutionProvider' in ort.get_available_providers():
        providers.append('CUDAExecutionProvider')
    providers.append('CPUExecutionProvider')
    
    # 14. 创建推理会话
    session = ort.InferenceSession(
        'runtime_model.onnx',
        sess_options=session_options,
        providers=providers
    )
    
    print(f"使用的执行Provider: {session.get_providers()}")
    
    # 15. 获取模型输入输出信息
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    
    print(f"\n模型输入: {inputs[0].name}, 形状: {inputs[0].shape}, 类型: {inputs[0].type}")
    print(f"模型输出: {outputs[0].name}, 形状: {outputs[0].shape}, 类型: {outputs[0].type}")
    
    # 16. 准备输入数据
    test_input = np.random.randn(1, 3, 32, 32).astype(np.float32)
    
    # 17. 运行推理
    output = session.run(None, {'input': test_input})[0]
    
    print(f"推理输出形状: {output.shape}")
    print(f"推理输出前3个值: {output[0][:3]}")
    
    return session

def optimized_onnx_runtime():
    """18. ONNX Runtime性能优化"""
    try:
        import onnxruntime as ort
    except ImportError:
        print("请安装ONNX Runtime")
        return
    
    # 19. 创建优化的会话选项
    session_options = ort.SessionOptions()
    
    # 20. 启用所有图优化
    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    
    # 21. 启用内存优化
    # 减少内存占用，特别适合大模型
    session_options.enable_mem_pattern = True
    session_options.enable_cpu_mem_arena = True
    
    # 22. 启用图序列化
    # 可以将优化后的图保存，避免重复优化
    session_options.optimized_model_filepath = 'optimized_model.onnx'
    
    # 23. 设置线程数
    # inter_op_parallelism: 并行执行不同节点的线程数
    # intra_op_parallelism: 单个节点内的线程数
    session_options.inter_op_parallelism_thread = 4
    session_options.intra_op_parallelism_thread = 4
    
    # 24. 创建会话
    session = ort.InferenceSession(
        'runtime_model.onnx',
        sess_options=session_options,
        providers=['CPUExecutionProvider']  # 根据实际情况选择
    )
    
    # 25. 性能测试
    import time
    
    test_input = np.random.randn(32, 3, 32, 32).astype(np.float32)
    
    # 26. 预热
    for _ in range(10):
        _ = session.run(None, {'input': test_input})
    
    # 27. 正式测试
    iterations = 100
    start = time.time()
    for _ in range(iterations):
        output = session.run(None, {'input': test_input})[0]
    elapsed = time.time() - start
    
    # 28. 计算性能指标
    throughput = iterations * test_input.shape[0] / elapsed
    latency = elapsed / iterations * 1000  # 毫秒
    
    print(f"\n=== ONNX Runtime 性能测试 ===")
    print(f"批次大小: {test_input.shape[0]}")
    print(f"总迭代次数: {iterations}")
    print(f"总耗时: {elapsed:.4f}秒")
    print(f"吞吐量: {throughput:.2f} samples/sec")
    print(f"延迟: {latency:.2f} ms/batch")
    
    return session

def cuda_onnx_runtime():
    """29. CUDA加速的ONNX Runtime"""
    try:
        import onnxruntime as ort
    except ImportError:
        return
    
    # 30. 检查可用的Provider
    available_providers = ort.get_available_providers()
    print(f"可用的Provider: {available_providers}")
    
    if 'CUDAExecutionProvider' not in available_providers:
        print("CUDA Provider 不可用")
        return
    
    # 31. CUDA Provider选项
    cuda_options = {
        'device_id': 0,              # GPU设备ID
        'arena_extend_strategy': 'kNextPowerOfTwo',  # 内存分配策略
        'gpu_mem_limit': 2 * 1024 * 1024 * 1024,  # 2GB内存限制
        'cudnn_conv_algo_search': 'EXHAUSTIVE',  # 卷积算法搜索策略
        'do_copy_in_default_stream': True,
    }
    
    # 32. 创建会话
    session_options = ort.SessionOptions()
    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    
    session = ort.InferenceSession(
        'runtime_model.onnx',
        sess_options=session_options,
        providers=[('CUDAExecutionProvider', cuda_options), 'CPUExecutionProvider']
    )
    
    print("✅ CUDA加速会话已创建")
    print(f"使用的Provider: {session.get_providers()}")
    
    return session

def benchmark_comparison():
    """33. PyTorch vs ONNX Runtime 性能对比"""
    try:
        import onnxruntime as ort
    except ImportError:
        print("请安装ONNX Runtime")
        return
    
    # 34. 创建PyTorch模型
    model = RuntimeTestModel()
    model.eval()
    
    # 35. ONNX Runtime会话
    session_options = ort.SessionOptions()
    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    ort_session = ort.InferenceSession('runtime_model.onnx', sess_options=session_options)
    
    # 36. 测试数据
    test_data = np.random.randn(16, 3, 32, 32).astype(np.float32)
    test_tensor = torch.from_numpy(test_data)
    
    iterations = 100
    
    # 37. PyTorch推理测试
    import time
    
    with torch.no_grad():
        # 预热
        for _ in range(10):
            _ = model(test_tensor)
        
        # 正式测试
        start = time.time()
        for _ in range(iterations):
            pt_output = model(test_tensor)
        pt_time = time.time() - start
    
    # 38. ONNX Runtime推理测试
    # 预热
    for _ in range(10):
        _ = ort_session.run(None, {'input': test_data})
    
    # 正式测试
    start = time.time()
    for _ in range(iterations):
        ort_output = ort_session.run(None, {'input': test_data})[0]
    ort_time = time.time() - start
    
    # 39. 打印对比结果
    print(f"\n=== PyTorch vs ONNX Runtime 性能对比 ===")
    print(f"PyTorch耗时: {pt_time:.4f}秒 ({iterations*16/pt_time:.0f} samples/sec)")
    print(f"ONNX Runtime耗时: {ort_time:.4f}秒 ({iterations*16/ort_time:.0f} samples/sec)")
    print(f"性能比: {pt_time/ort_time:.2f}x")

if __name__ == "__main__":
    # 40. 测试ONNX Runtime功能
    onnx_model_path = export_for_runtime()
    basic_onnx_runtime_inference()
    optimized_onnx_runtime()
    benchmark_comparison()
