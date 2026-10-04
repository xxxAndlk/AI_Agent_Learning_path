import faiss
import numpy as np
import time

# 检查GPU可用性
print("GPU数量:", faiss.get_num_gpus())

# 创建GPU索引
d = 128
n = 1000000

xb = np.random.random((n, d)).astype('float32')
xq = np.random.random((100, d)).astype('float32')

# 创建CPU索引作为基础
index = faiss.IndexFlatL2(d)

# 转换为GPU索引
# gpu_id: GPU设备编号（0是第一块GPU）
gpu_index = faiss.index_cpu_to_gpu(
    faiss.StandardGpuResources(),  # GPU资源管理器
    0,                              # GPU设备ID
    index
)

# 添加向量
gpu_index.add(xb)

# 搜索
start = time.time()
D, I = gpu_index.search(xq, k=10)
print(f"GPU搜索耗时: {(time.time()-start)/len(xq)*1000:.2f} ms/查询")
