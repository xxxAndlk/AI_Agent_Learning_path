import faiss
import numpy as np
import time

# ============ HNSW索引完整示例 ============

# 参数配置
d = 128                      # 向量维度
nb = 100000                  # 数据库规模（10万）
nq = 100                     # 查询数量
k = 10                       # 返回top-k
M = 32                       # 每个节点的连接数
efConstruction = 40          # 建索引时的搜索宽度
efSearch = 16                # 搜索时的搜索宽度

# 生成测试数据
np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

print("=" * 60)
print("HNSW索引演示")
print("=" * 60)

# 创建HNSW索引
# 参数：维度、每个节点的连接数(M)、efConstruction
index_hnsw = faiss.IndexHNSWFlat(d, M)
index_hnsw.hnsw.efConstruction = efConstruction
index_hnsw.hnsw.efSearch = efSearch

print(f"参数配置: M={M}, efConstruction={efConstruction}, efSearch={efSearch}")

# 添加向量
start_time = time.time()
index_hnsw.add(xb)
add_time = time.time() - start_time
print(f"添加 {index_hnsw.ntotal} 个向量耗时: {add_time:.2f}秒")

# 执行搜索
start_time = time.time()
D, I = index_hnsw.search(xq, k)
search_time = time.time() - start_time

print(f"\n搜索耗时: {search_time:.4f}秒")
print(f"平均单次查询: {search_time/nq*1000:.2f}ms")
print(f"吞吐量: {nq/search_time:.2f} QPS")

# 展示第一个查询结果
print(f"\n第一个查询的top-{k}结果:")
print(f"索引: {I[0]}")
print(f"距离: {D[0]}")
