import faiss
import numpy as np
import time

# 创建测试数据
d = 128                      # 向量维度
n = 100000                   # 向量数量
np.random.seed(42)
xb = np.random.random((n, d)).astype('float32')

# 创建Flat L2索引
index_flat = faiss.IndexFlatL2(d)

# 添加向量并计时
start_time = time.time()
index_flat.add(xb)
add_time = time.time() - start_time
print(f"添加 {n} 个向量耗时: {add_time:.3f} 秒")

# 创建查询向量
nq = 100
xq = np.random.random((nq, d)).astype('float32')

# 执行搜索并计时
k = 10
start_time = time.time()
D, I = index_flat.search(xq, k)
search_time = time.time() - start_time
print(f"查询 {nq} 次，每次返回 Top-{k}:")
print(f"  总耗时: {search_time:.3f} 秒")
print(f"  平均耗时: {search_time/nq*1000:.2f} ms/查询")
print(f"  QPS: {nq/search_time:.1f}")
