def onnx_export():
    """ONNX导出"""
    
    model = SimpleModel()
    model.eval()
    
    # 创建示例输入（ONNX要求固定batch_size）
    dummy_input = torch.randn(1, 3, 32, 32)
    
    # 导出为ONNX
    torch.onnx.export(
        model,
        dummy_input,
        'model.onnx',
        export_params=True,        # 导出参数
        opset_version=13,          # ONNX算子版本
        do_constant_folding=True,  # 常量折叠优化
        input_names=['input'],     # 输入名称
        output_names=['output'],   # 输出名称
        dynamic_axes={
            'input': {0: 'batch_size'},  # 动态batch维度
            'output': {0: 'batch_size'}
        }
    )
    
    print("ONNX模型已导出到 model.onnx")
    
    # 验证ONNX模型
    import onnx
    onnx_model = onnx.load('model.onnx')
    onnx.checker.check_model(onnx_model)
    print("ONNX模型验证通过")
    
    # 使用ONNX Runtime推理
    try:
        import onnxruntime as ort
        
        # 创建推理会话
        ort_session = ort.InferenceSession('model.onnx')
        
        # 准备输入
        ort_inputs = {'input': dummy_input.numpy()}
        
        # 推理
        ort_outputs = ort_session.run(None, ort_inputs)
        
        print(f"ONNX Runtime输出: {ort_outputs[0].shape}")
        
    except ImportError:
        print("请安装onnxruntime: pip install onnxruntime")
    
    # 对比PyTorch输出
    with torch.no_grad():
        torch_output = model(dummy_input)
    
    print(f"PyTorch输出与ONNX输出的差异: {torch.max(torch.abs(torch_output - torch.tensor(ort_outputs[0]))).item()}")

import numpy
