import faiss
import numpy as np

# FAISS基础使用
d = 128                      # 向量维度
nb = 100000                  # 数据库规模

# 创建索引
index = faiss.IndexFlatL2(d)

# 添加向量
xb = np.random.random((nb, d)).astype('float32')
index.add(xb)

# 搜索
xq = np.random.random((10, d)).astype('float32')
D, I = index.search(xq, k=5)

print(f"搜索到 {len(I)} 个结果")
