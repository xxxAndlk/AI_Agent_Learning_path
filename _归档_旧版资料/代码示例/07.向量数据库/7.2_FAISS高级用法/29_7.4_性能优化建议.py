"""
FAISS性能优化最佳实践
"""

# 1. 批量处理优化
def batch_optimization():
    """批量处理优化示例"""
    import faiss
    import numpy as np
    
    d = 128
    n = 1000000
    
    # 坏的做法：逐个查询
    index = faiss.IndexFlatL2(d)
    index.add(np.random.random((n, d)).astype('float32'))
    
    xq = np.random.random((100, d)).astype('float32')
    
    # 逐个查询
    import time
    start = time.time()
    for q in xq:
        index.search(q.reshape(1, -1), k=10)
    single_time = time.time() - start
    
    # 批量查询
    start = time.time()
    index.search(xq, k=10)
    batch_time = time.time() - start
    
    print(f"逐个查询: {single_time:.3f}s")
    print(f"批量查询: {batch_time:.3f}s")
    print(f"加速比: {single_time/batch_time:.1f}x")


# 2. 内存优化
def memory_optimization():
    """内存优化示例"""
    import faiss
    import numpy as np
    
    d = 128
    n = 1000000
    
    # float32 vs float64
    vectors_f32 = np.random.random((n, d)).astype('float32')
    vectors_f64 = np.random.random((n, d)).astype('float64')
    
    print(f"float32 内存: {vectors_f32.nbytes / 1024 / 1024:.1f} MB")
    print(f"float64 内存: {vectors_f64.nbytes / 1024 / 1024:.1f} MB")
    print("建议：始终使用 float32")


# 3. IVF训练数据采样
def training_optimization():
    """训练数据优化"""
    import faiss
    import numpy as np
    
    d = 128
    n = 10000000  # 1000万向量
    
    # 全量训练
    xb_full = np.random.random((n, d)).astype('float32')
    index_full = faiss.IndexIVFFlat(faiss.IndexFlatL2(d), d, 100)
    
    start = time.time()
    index_full.train(xb_full)
    print(f"全量训练({n}): {time.time()-start:.2f}s")
    
    # 采样训练（推荐）
    sample_size = min(100000, n)
    xb_sample = xb_full[:sample_size]
    index_sample = faiss.IndexIVFFlat(faiss.IndexFlatL2(d), d, 100)
    
    start = time.time()
    index_sample.train(xb_sample)
    print(f"采样训练({sample_size}): {time.time()-start:.2f}s")
    print("注意：采样训练可能导致聚类中心偏移，适合大规模数据")


# 运行优化演示
batch_optimization()
memory_optimization()
training_optimization()
