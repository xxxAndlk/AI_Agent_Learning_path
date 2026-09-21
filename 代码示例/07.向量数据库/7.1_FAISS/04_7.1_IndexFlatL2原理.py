import faiss
import numpy as np
import time

# ============ Flat索引完整示例 ============

# 参数设置
d = 128              # 向量维度
nb = 100000          # 数据库向量数量（10万）
nq = 100             # 查询向量数量
k = 10               # 返回top-k结果

# 生成测试数据
np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

# 创建IndexFlatL2索引
index = faiss.IndexFlatL2(d)

print("=" * 60)
print("IndexFlatL2 索引演示")
print("=" * 60)
print(f"向量维度: {d}")
print(f"数据库规模: {nb}")
print(f"查询数量: {nq}")
print(f"返回结果数: {k}")

# 添加向量
start_time = time.time()
index.add(xb)
add_time = time.time() - start_time
print(f"\n添加 {index.ntotal} 个向量耗时: {add_time:.4f}秒")

# 执行搜索并计时
start_time = time.time()
D, I = index.search(xq, k)
search_time = time.time() - start_time

print(f"搜索耗时: {search_time:.4f}秒")
print(f"平均单次查询耗时: {search_time/nq*1000:.2f}ms")
print(f"吞吐量: {nq/search_time:.2f} QPS")

# 展示第一个查询的结果
print("\n第一个查询的top-{}结果:".format(k))
print("索引:", I[0])
print("距离:", D[0])
