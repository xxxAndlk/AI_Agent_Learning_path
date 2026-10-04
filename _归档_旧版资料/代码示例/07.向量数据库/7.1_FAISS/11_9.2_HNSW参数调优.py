import faiss
import numpy as np
import time

# ============ HNSW参数调优示例 ============

d = 128
nb = 50000
nq = 50
k = 10

np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

# 计算真实最近邻（基准）
index_flat = faiss.IndexFlatL2(d)
index_flat.add(xb)
D_flat, I_flat = index_flat.search(xq, k)

print("=" * 60)
print("HNSW参数调优")
print("=" * 60)

# 测试不同M和efSearch组合
configs = [
    (8, 16),
    (16, 16),
    (32, 16),
    (32, 32),
    (32, 64),
    (64, 64),
]

print(f"{'M':<6} {'efSearch':<10} {'耗时(ms)':<12} {'召回率':<10}")
print("-" * 45)

for M, efSearch in configs:
    index = faiss.IndexHNSWFlat(d, M)
    index.hnsw.efConstruction = 40
    index.hnsw.efSearch = efSearch
    index.add(xb)
    
    start = time.time()
    D, I = index.search(xq, k)
    elapsed = time.time() - start
    
    # 计算召回率
    recall = sum(
        len(set(I_flat[i]) & set(I[i])) 
        for i in range(nq)
    ) / (nq * k)
    
    print(f"{M:<6} {efSearch:<10} {elapsed*1000/nq:<12.2f} {recall*100:<10.2f}%")
