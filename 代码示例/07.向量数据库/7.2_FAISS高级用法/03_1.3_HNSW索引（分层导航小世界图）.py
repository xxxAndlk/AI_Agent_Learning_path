import faiss
import numpy as np
import time

# HNSW参数说明
# M: 每个节点的连接数，越大索引越精确但内存占用越高
# efConstruction: 构建时的搜索宽度，越大构建越慢但索引质量越高
# efSearch: 搜索时的搜索宽度，越大搜索越精确但速度越慢

d = 128
n = 1000000

np.random.seed(42)
xb = np.random.random((n, d)).astype('float32')

# 创建HNSW索引
# M=32: 每个节点32个连接
# efConstruction=40: 构建时搜索宽度
index_hnsw = faiss.IndexHNSWFlat(d, 32)
index_hnsw.hnsw.efConstruction = 40

print("开始构建HNSW索引...")
start_time = time.time()
index_hnsw.add(xb)
build_time = time.time() - start_time
print(f"构建耗时: {build_time:.2f} 秒")

# 测试不同efSearch参数
nq = 100
xq = np.random.random((nq, d)).astype('float32')

print("\n不同efSearch参数的性能:")
for ef in [16, 32, 64, 128, 256]:
    index_hnsw.hnsw.efSearch = ef
    
    start_time = time.time()
    D, I = index_hnsw.search(xq, k=10)
    search_time = time.time() - start_time
    
    print(f"efSearch={ef:3d}: 耗时 {search_time:.3f}s, "
          f"QPS={nq/search_time:.1f}")
