import faiss
import numpy as np

# 多GPU配置
ngpu = 4  # 使用4块GPU

# 创建resources数组
resources = [faiss.StandardGpuResources() for _ in range(ngpu)]

# 创建多个GPU索引
d = 128
nlist = 256

# 使用GpuClonerInvertedLists进行数据分片
index = faiss.IndexIVFFlat(faiss.IndexFlatL2(d), d, nlist)

# 配置多GPU参数
config = faiss.GpuMultipleClonerOptions()
config.shard = True  # 数据分片到不同GPU

# 转换为多GPU索引
gpu_index = faiss.index_cpu_to_gpu_multiple(
    resources,  # GPU资源数组
    index,
    config
)

print(f"使用 {faiss.get_num_gpus()} 块GPU")
