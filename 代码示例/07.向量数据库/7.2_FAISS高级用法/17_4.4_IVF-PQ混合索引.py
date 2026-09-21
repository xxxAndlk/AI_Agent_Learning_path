import faiss
import numpy as np
import time

def create_ivf_pq_index(d, nlist, m, nbits):
    """创建IVF-PQ索引"""
    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits)
    return index

# 测试IVF-PQ性能
d = 128
n = 1000000

np.random.seed(42)
xb = np.random.random((n, d)).astype('float32')
xq = np.random.random((100, d)).astype('float32')

# 参考索引
index_ref = faiss.IndexFlatL2(d)
index_ref.add(xb[:10000])
D_ref, I_ref = index_ref.search(xq, k=10)

print("=== IVF-PQ 性能测试 ===\n")

configs = [
    (100, 8, 8),
    (100, 8, 12),
    (256, 8, 8),
    (256, 16, 8),
]

for nlist, m, nbits in configs:
    index = create_ivf_pq_index(d, nlist, m, nbits)
    
    start = time.time()
    index.train(xb)
    train_time = time.time() - start
    
    start = time.time()
    index.add(xb)
    add_time = time.time() - start
    
    # 测试不同nprobe
    for nprobe in [1, 10, 20]:
        index.nprobe = nprobe
        
        start = time.time()
        D, I = index.search(xq, k=10)
        search_time = time.time() - start
        
        recall = np.mean([
            len(set(I[i]) & set(I_ref[i])) / 10 
            for i in range(100)
        ])
        
        print(f"nlist={nlist:3d}, m={m}, nbits={nbits}, "
              f"nprobe={nprobe:2d} | 召回: {recall:.2%} | "
              f"搜索: {search_time*10:.1f}ms")
