def mixed_precision_basics():
    """混合精度基础"""
    
    # FP16 (Float16): 1位符号, 5位指数, 10位尾数
    # 范围: ±6.55e±5, 精度: ~3-4位小数
    # 优点: 显存减半，加速明显
    # 缺点: 数值范围小，可能溢出
    
    # BF16 (BFloat16): 1位符号, 8位指数, 7位尾数
    # 范围: ±3.39e±38 (与FP32相同), 精度: ~2-3位小数
    # 优点: 数值范围大，溢出风险低
    # 缺点: 精度略低
    
    # 检查硬件支持
    print(f"CUDA支持: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        # 检查TF32支持（ Ampere架构+）
        print(f"TF32支持: {torch.backends.cuda.matmul.allow_tf32}")
        print(f"cuDNN TF32: {torch.backends.cudnn.allow_tf32}")
        
        # 检查FP16支持
        print(f"FP16支持: {torch.cuda.has_half}")
        
        # 检查BF16支持（从PyTorch 1.10+）
        try:
            print(f"BF16支持: {torch.cuda.is_bf16_supported()}")
        except:
            print("BF16支持: 需要PyTorch 1.10+")

# 创建BF16张量
def bf16_example():
    """BF16使用示例"""
    if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
        x = torch.randn(100, 100, dtype=torch.bfloat16, device='cuda')
        print(f"BF16张量: {x.dtype}")
        
        # 混合精度训练
        x_fp32 = x.float()  # 转FP32进行计算
        y = x_fp32 @ x_fp32
        print(f"结果类型: {y.dtype}")
