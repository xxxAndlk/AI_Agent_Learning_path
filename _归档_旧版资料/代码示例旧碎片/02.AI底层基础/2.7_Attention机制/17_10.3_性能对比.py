def sparse_attention_benchmark():
    """对比不同稀疏模式的性能"""
    device = torch.device('cuda')
    
    batch_size = 2
    d_model = 512
    num_heads = 8
    seq_len = 4096
    
    # 标准注意力
    standard_attn = MultiHeadAttention(d_model, num_heads).to(device)
    
    # 各种稀疏注意力
    fixed_attn = SparseAttention(d_model, num_heads, 
                                 global_tokens=8, sparse_type='fixed').to(device)
    local_attn = SparseAttention(d_model, num_heads, 
                                 window_size=128, sparse_type='global_local').to(device)
    block_attn = BlockSparseAttention(d_model, num_heads, 
                                      block_size=64, num_local_blocks=2).to(device)
    
    x = torch.randn(batch_size, seq_len, d_model).to(device)
    
    # 预热
    with torch.no_grad():
        for _ in range(2):
            _ = standard_attn(x, x, x)
            _ = fixed_attn(x)
            _ = local_attn(x)
            _ = block_attn(x)
    
    torch.cuda.synchronize()
    
    import time
    
    # 计时
    results = {}
    
    for name, model in [('Standard', standard_attn), 
                        ('Fixed', fixed_attn),
                        ('Global+Local', local_attn),
                        ('Block Sparse', block_attn)]:
        start = time.time()
        with torch.no_grad():
            for _ in range(5):
                _ = model(x)
        torch.cuda.synchronize()
        results[name] = (time.time() - start) / 5
        print(f"{name}: {results[name]:.4f}s")
    
    # 计算复杂度
    n = seq_len
    print(f"\n计算复杂度分析:")
    print(f"标准注意力: O(n²) = {n*n:,} 操作")
    print(f"Fixed: O(n·g) = {n*8:,} 操作 (g=8全局token)")
    print(f"Global+Local: O(n·w) = {n*128:,} 操作 (w=128窗口)")
    print(f"Block Sparse: O(n·b) = {n*128:,} 操作 (b=2块)")
    
    return results

# 输出示例:
# Standard: 0.1523s
# Fixed: 0.0412s (3.7x加速)
# Global+Local: 0.0389s (3.9x加速)
# Block Sparse: 0.0356s (4.3x加速)
