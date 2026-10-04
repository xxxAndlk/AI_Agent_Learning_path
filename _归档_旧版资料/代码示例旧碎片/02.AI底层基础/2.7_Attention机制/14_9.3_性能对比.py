def benchmark_attention():
    """对比标准注意力和线性注意力的性能"""
    import time
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 测试配置
    batch_size = 4
    num_heads = 8
    d_model = 512
    seq_lengths = [256, 512, 1024, 2048, 4096]
    
    # 创建模型
    standard_attn = MultiHeadAttention(d_model, num_heads).to(device)
    linear_attn = LinearAttention(d_model, num_heads, kernel_type='relu').to(device)
    
    results = {'seq_len': [], 'standard_time': [], 'linear_time': [], 'speedup': []}
    
    for seq_len in seq_lengths:
        x = torch.randn(batch_size, seq_len, d_model).to(device)
        
        # 预热
        with torch.no_grad():
            _ = standard_attn(x, x, x)
            _ = linear_attn(x)
        
        torch.cuda.synchronize()
        
        # 标准注意力计时
        start = time.time()
        with torch.no_grad():
            for _ in range(3):
                _ = standard_attn(x, x, x)
        torch.cuda.synchronize()
        standard_time = (time.time() - start) / 3
        
        # 线性注意力计时
        start = time.time()
        with torch.no_grad():
            for _ in range(3):
                _ = linear_attn(x)
        torch.cuda.synchronize()
        linear_time = (time.time() - start) / 3
        
        results['seq_len'].append(seq_len)
        results['standard_time'].append(standard_time)
        results['linear_time'].append(linear_time)
        results['speedup'].append(standard_time / linear_time)
        
        print(f"Seq len: {seq_len:5d} | Standard: {standard_time:.4f}s | "
              f"Linear: {linear_time:.4f}s | Speedup: {results['speedup'][-1]:.2f}x")
    
    return results

# 输出示例：
# Seq len:  256 | Standard: 0.0021s | Linear: 0.0018s | Speedup: 1.17x
# Seq len:  512 | Standard: 0.0058s | Linear: 0.0032s | Speedup: 1.81x
# Seq len: 1024 | Standard: 0.0189s | Linear: 0.0058s | Speedup: 3.26x
# Seq len: 2048 | Standard: 0.0672s | Linear: 0.0105s | Speedup: 6.40x
# Seq len: 4096 | Standard: 0.2451s | Linear: 0.0198s | Speedup: 12.38x
