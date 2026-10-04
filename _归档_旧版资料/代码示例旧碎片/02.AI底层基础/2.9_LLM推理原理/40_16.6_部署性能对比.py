"""
边缘部署性能对比
"""

def compare_edge_deployment():
    """对比不同边缘部署方案的性能"""
    
    deployments = [
        {"name": "llama.cpp Q4 (CPU)", "device": "CPU", "quant": "Q4"},
        {"name": "llama.cpp Q4 (GPU)", "device": "RTX 3090", "quant": "Q4"},
        {"name": "ONNX INT8", "device": "CPU", "quant": "INT8"},
        {"name": "TensorRT FP16", "device": "A100", "quant": "FP16"},
        {"name": "MLC-LLM (WebGPU)", "device": "Browser", "quant": "Q4"},
    ]
    
    # 预期性能（7B模型，512 tokens生成）
    """
    部署方案          │ 设备        │ 首Token │ 吞吐量    │ 内存占用
    ─────────────────┼─────────────┼─────────┼──────────┼─────────
    llama.cpp Q4     │ AMD 5800X   │ 2.5s    │ 8 tok/s  │ 4GB
    llama.cpp Q4     │ RTX 3090    │ 0.5s    │ 35 tok/s │ 4GB
    ONNX INT8        │ Intel i9    │ 3.0s    │ 12 tok/s │ 3.5GB
    TensorRT FP16    │ A100        │ 0.3s    │ 80 tok/s │ 14GB
    MLC WebGPU       │ Chrome/M1   │ 1.5s    │ 15 tok/s │ 3GB
    """
    
    print("边缘部署性能对比：")
    print("设备: 7B参数模型")
    print("-" * 60)
    
    for d in deployments:
        print(f"{d['name']:20s} | {d['device']:10s} | 依硬件而定")
