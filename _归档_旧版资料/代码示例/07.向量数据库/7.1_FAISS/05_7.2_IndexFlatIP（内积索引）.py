import faiss
import numpy as np

# ============ IndexFlatIP（内积索引）示例 ============

d = 64                     # 向量维度
nb = 1000                  # 向量数量

# 生成归一化的测试向量
np.random.seed(123)
xb = np.random.random((nb, d)).astype('float32')

# 归一化向量（使内积等价于余弦相似度）
norms = np.linalg.norm(xb, axis=1, keepdims=True)
xb_normalized = xb / norms

# 创建内积索引
index = faiss.IndexFlatIP(d)

# 添加归一化后的向量
index.add(xb_normalized)

print(f"索引类型: IndexFlatIP (内积)")
print(f"向量数量: {index.ntotal}")

# 查询向量
xq = np.random.random((1, d)).astype('float32')
xq_normalized = xq / np.linalg.norm(xq)

# 搜索（返回的"距离"实际是内积值，越大越相似）
k = 5
D, I = index.search(xq_normalized, k)

print(f"\n查询向量的top-{k}相似结果:")
for i in range(k):
    print(f"  排名{i+1}: 索引={I[0][i]}, 内积(相似度)={D[0][i]:.4f}")
