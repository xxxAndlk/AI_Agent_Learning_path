import faiss
import numpy as np

def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    """L2归一化向量"""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms

def choose_distance_metric(use_cosine: bool = True) -> str:
    """
    选择距离度量
    
    参数:
        use_cosine: 是否使用余弦相似度
        
    返回:
        推荐的度量方式和说明
    """
    if use_cosine:
        return "内积 (需要先归一化，等价于余弦相似度)"
    else:
        return "L2距离 (欧几里得距离)"

# 示例：归一化与内积搜索
print("=" * 60)
print("距离度量对比")
print("=" * 60)

d = 64
nb = 1000
np.random.seed(42)

# 创建测试向量
vectors = np.random.random((nb, d)).astype('float32')

# 方法1：使用L2距离
index_l2 = faiss.IndexFlatL2(d)
index_l2.add(vectors)
query = np.random.random(d).astype('float32')
D_l2, I_l2 = index_l2.search(query.reshape(1, -1), k=5)

print("\nL2距离搜索结果:")
print(f"最近邻索引: {I_l2[0]}")
print(f"对应距离: {D_l2[0]}")

# 方法2：使用内积（归一化后等价于余弦相似度）
vectors_norm = normalize_vectors(vectors)
query_norm = normalize_vectors(query.reshape(1, -1))

index_ip = faiss.IndexFlatIP(d)
index_ip.add(vectors_norm)
D_ip, I_ip = index_ip.search(query_norm, k=5)

print("\n内积搜索结果（归一化后=余弦相似度）:")
print(f"最近邻索引: {I_ip[0]}")
print(f"对应内积值: {D_ip[0]}")
