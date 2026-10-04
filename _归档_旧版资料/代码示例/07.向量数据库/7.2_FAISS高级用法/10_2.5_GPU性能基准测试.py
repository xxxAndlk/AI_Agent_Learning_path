import faiss
import numpy as np
import time

def benchmark_cpu_vs_gpu(d, n, nq=100):
    """CPU vs GPU性能对比"""
    np.random.seed(42)
    xb = np.random.random((n, d)).astype('float32')
    xq = np.random.random((nq, d)).astype('float32')
    
    # CPU索引
    index_cpu = faiss.IndexFlatL2(d)
    index_cpu.add(xb)
    
    start = time.time()
    D_cpu, I_cpu = index_cpu.search(xq, k=10)
    cpu_time = (time.time() - start) / nq * 1000
    
    # GPU索引
    if faiss.get_num_gpus() > 0:
        index_gpu = faiss.index_cpu_to_gpu(
            faiss.StandardGpuResources(), 0,
            faiss.IndexFlatL2(d)
        )
        index_gpu.add(xb)
        
        start = time.time()
        D_gpu, I_gpu = index_gpu.search(xq, k=10)
        gpu_time = (time.time() - start) / nq * 1000
        
        speedup = cpu_time / gpu_time
        print(f"数据量: {n:8d} | CPU: {cpu_time:6.2f}ms | "
              f"GPU: {gpu_time:6.2f}ms | 加速比: {speedup:.1f}x")
    else:
        print(f"数据量: {n:8d} | CPU: {cpu_time:6.2f}ms | GPU: 不可用")

print("=== CPU vs GPU 性能对比 ===")
print(f"维度: 128, 查询数: 100, Top-K: 10\n")

for n in [10000, 100000, 1000000, 5000000]:
    benchmark_cpu_vs_gpu(128, n)
