import faiss
import numpy as np

# 检查GPU是否可用
gpu_resources = faiss.StandardGpuResources()

# 创建GPU索引
d = 128  # 向量维度
index = faiss.IndexFlatL2(d)

# 将CPU索引转换为GPU索引
gpu_index = faiss.index_cpu_to_gpu(gpu_resources, 0, index)

# 添加向量
nb = 10000
xb = np.random.random((nb, d)).astype('float32')
gpu_index.add(xb)

# 搜索
nq = 5
xq = np.random.random((nq, d)).astype('float32')
distances, indices = gpu_index.search(xq, k=5)

print(f"GPU索引包含 {gpu_index.ntotal} 个向量")
print("GPU加速搜索完成！")
