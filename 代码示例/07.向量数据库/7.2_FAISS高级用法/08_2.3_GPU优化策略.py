import faiss
import numpy as np
import time

def create_gpu_ivf_index(d, nlist, use_gpu=True):
    """创建优化的GPU IVF索引"""
    # 量化器
    quantizer = faiss.IndexFlatL2(d)
    
    # IVF索引
    index = faiss.IndexIVFFlat(quantizer, d, nlist)
    
    if use_gpu:
        # 转换为GPU索引，带优化参数
        # 使用更短的 floats 减少传输时间
        index = faiss.index_cpu_to_gpu(
            faiss.StandardGpuResources(),
            0,
            index,
            faiss.GpuIndexFlatConfig(),
            faiss.GpuIVFFlatConfig()
        )
    
    return index

# 大规模数据测试
d = 128
n = 5000000  # 500万向量
nlist = 512  # 聚类数

np.random.seed(42)
xb = np.random.random((n, d)).astype('float32')
xq = np.random.random((100, d)).astype('float32')

# 创建GPU索引
print("创建GPU IVF索引...")
index = create_gpu_ivf_index(d, nlist, use_gpu=True)

# 训练
print("训练中...")
start = time.time()
index.train(xb)
print(f"训练耗时: {time.time()-start:.2f}s")

# 添加向量
print("添加向量...")
start = time.time()
index.add(xb)
print(f"添加耗时: {time.time()-start:.2f}s")

# 搜索性能
print("搜索性能测试...")
index.nprobe = 20
start = time.time()
D, I = index.search(xq, k=10)
elapsed = time.time() - start
print(f"GPU搜索: {elapsed/100*1000:.2f} ms/query, QPS: {100/elapsed:.1f}")
