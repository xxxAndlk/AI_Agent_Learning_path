# 综合对比演示
import faiss
import numpy as np
import time
import psutil

def benchmark_index(index_name, index, xb, xq, k=10):
    """基准测试函数"""
    # 添加数据
    index.add(xb)
    
    # 预热
    index.search(xq[:10], k)
    
    # 搜索测试
    nq = len(xq)
    start = time.time()
    D, I = index.search(xq, k)
    search_time = time.time() - start
    
    # 内存估算
    process = psutil.Process()
    mem_mb = process.memory_info().rss / 1024 / 1024
    
    return {
        'name': index_name,
        'search_time': search_time / nq * 1000,  # ms per query
        'qps': nq / search_time,
        'memory_mb': mem_mb
    }

# 测试配置
d = 128
n = 500000
np.random.seed(42)
xb = np.random.random((n, d)).astype('float32')
xq = np.random.random((100, d)).astype('float32')

results = []

# Flat索引
idx = faiss.IndexFlatL2(d)
results.append(benchmark_index('Flat', idx, xb, xq))

# IVF索引
quantizer = faiss.IndexFlatL2(d)
idx = faiss.IndexIVFFlat(quantizer, d, 100)
idx.train(xb)
results.append(benchmark_index('IVF-Flat(nprobe=10)', idx, xb, xq))

# HNSW索引
idx = faiss.IndexHNSWFlat(d, 16)
results.append(benchmark_index('HNSW(M=16)', idx, xb, xq))

# PQ索引
idx = faiss.IndexPQ(d, 8, 8)
idx.train(xb)
results.append(benchmark_index('PQ(8×8)', idx, xb, xq))

# 打印结果
print("\n=== 50万向量索引性能对比 ===")
print(f"{'索引类型':<20} {'查询时间(ms)':<15} {'QPS':<12} {'内存(MB)':<12}")
print("-" * 60)
for r in results:
    print(f"{r['name']:<20} {r['search_time']:<15.2f} "
          f"{r['qps']:<12.1f} {r['memory_mb']:<12.1f}")
