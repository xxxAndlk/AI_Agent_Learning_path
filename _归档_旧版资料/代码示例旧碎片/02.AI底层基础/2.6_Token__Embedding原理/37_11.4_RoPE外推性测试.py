def test_rope_extrapolation():
    """测试RoPE的外推能力"""
    
    # 训练时最长512，测试更长序列
    max_train_len = 512
    test_seq_len = 1024
    
    dim = 64
    
    # 创建输入
    x = torch.randn(1, test_seq_len, dim)
    
    # 创建RoPE（模拟训练时固定长度）
    rope = RoPE(dim, max_seq_len=max_train_len)
    
    # 外推测试
    try:
        output = rope(x, seq_len=test_seq_len)
        print(f"✓ 成功处理长度{test_seq_len}的序列（训练时最长{max_train_len}）")
        print(f"  输出形状: {output.shape}")
    except Exception as e:
        print(f"✗ 外推失败: {e}")
    
    # RoPE的优势：可以处理超过训练长度的序列
    # 因为旋转角度是连续计算的，不需要额外参数

test_rope_extrapolation()
