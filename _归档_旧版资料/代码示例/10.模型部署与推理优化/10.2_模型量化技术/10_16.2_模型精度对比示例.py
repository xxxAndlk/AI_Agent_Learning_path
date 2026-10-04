def compare_quantization_methods():
    """对比不同量化方法的精度"""
    import torchvision.models as models
    
    # 加载预训练模型
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.eval()
    
    # 准备测试数据
    test_input = torch.randn(100, 3, 224, 224)
    
    # 测试不同量化方法
    results = {}
    
    # FP32基准
    print("测试 FP32...")
    with torch.no_grad():
        fp32_output = model(test_input)
    results['FP32'] = fp32_output.abs().mean().item()
    
    # 动态INT8量化
    print("测试 INT8 动态量化...")
    int8_model = torch.quantization.quantize_dynamic(
        model, {nn.Linear, nn.Conv2d}, dtype=torch.qint8
    )
    with torch.no_grad():
        int8_output = int8_model(test_input)
    results['INT8'] = int8_output.abs().mean().item()
    
    # 打印对比结果
    print("\n=== 量化精度对比 ===")
    baseline = results['FP32']
    for method, value in results.items():
        diff_pct = abs(value - baseline) / baseline * 100
        print(f"{method}: {value:.4f}, 差异: {diff_pct:.2f}%")
