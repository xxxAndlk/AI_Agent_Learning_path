import faiss
import numpy as np

# faiss模块未提供__version__属性，用getattr安全读取（版本可用pip show faiss-cpu查询）
print(f"FAISS版本: {getattr(faiss, '__version__', '未提供（可用pip show faiss-cpu查询）')}")

# 创建一个简单的索引测试
d = 64  # 向量维度
index = faiss.IndexFlatL2(d)

# 创建测试向量
x = np.random.random((10, d)).astype('float32')

# 添加向量
index.add(x)

# 搜索
k = 3  # 返回3个最近邻
query = np.random.random((1, d)).astype('float32')
distances, indices = index.search(query, k)

print(f"索引包含 {index.ntotal} 个向量")
print(f"搜索成功！找到 {k} 个最近邻")
print(f"距离: {distances}")
print(f"索引: {indices}")
