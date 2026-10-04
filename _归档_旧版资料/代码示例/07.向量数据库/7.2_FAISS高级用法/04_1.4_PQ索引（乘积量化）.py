import faiss
import numpy as np
import time

# PQ参数
# m: 子向量数量，通常设为4、8、16、32等
# nbits: 每个子向量的编码位数，通常设为8、12、16

d = 128
n = 1000000

np.random.seed(42)
xb = np.random.random((n, d)).astype('float32')

# 创建PQ索引
# m=8: 分割为8个子向量
# nbits=8: 每个子向量用8位编码（256个码字）
index_pq = faiss.IndexPQ(d, 8, 8)

print("开始训练PQ索引...")
start_time = time.time()
index_pq.train(xb)
train_time = time.time() - start_time
print(f"训练耗时: {train_time:.2f} 秒")

print("开始添加向量...")
start_time = time.time()
index_pq.add(xb)
add_time = time.time() - start_time
print(f"添加耗时: {add_time:.2f} 秒")

# 搜索测试
nq = 100
xq = np.random.random((nq, d)).astype('float32')

start_time = time.time()
D, I = index_pq.search(xq, k=10)
search_time = time.time() - start_time
print(f"搜索耗时: {search_time:.3f}s, QPS: {nq/search_time:.1f}")

# 对比存储空间
print(f"\n原始向量存储: {n * d * 4 / 1024 / 1024:.1f} MB")
print(f"PQ编码存储: {index_pq.sa_code_size() * n / 8 / 1024 / 1024:.1f} MB")
