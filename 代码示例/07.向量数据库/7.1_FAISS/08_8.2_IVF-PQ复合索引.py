import faiss
import numpy as np
import time

# ============ IVF-PQ索引示例 ============

# 参数配置
d = 128                      # 向量维度
nb = 100000                  # 数据库规模
nq = 100                     # 查询数量
k = 10                       # 返回top-k
nlist = 100                  # IVF聚类数量
m = 8                        # PQ子向量数量（维度被分割为m份）
nbits = 8                    # 每个子向量的编码位数

# 生成测试数据
np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

print("=" * 60)
print("IVF-PQ索引演示（高压缩率）")
print("=" * 60)

# 创建量化器
quantizer = faiss.IndexFlatL2(d)

# 创建IVF-PQ索引
# 参数：量化器、维度、聚类数、子向量数、编码位数、距离度量
index_pq = faiss.IndexIVFPQ(
    quantizer, 
    d, 
    nlist, 
    m, 
    nbits, 
    faiss.METRIC_L2
)

# 训练索引
print("开始训练...")
start_time = time.time()
index_pq.train(xb)
print(f"训练耗时: {time.time() - start_time:.2f}秒")

# 添加向量
start_time = time.time()
index_pq.add(xb)
add_time = time.time() - start_time
print(f"添加 {index_pq.ntotal} 个向量耗时: {add_time:.2f}秒")

# 设置搜索参数
index_pq.nprobe = 10

# 搜索
start_time = time.time()
D, I = index_pq.search(xq, k)
search_time = time.time() - start_time

print(f"搜索耗时: {search_time:.4f}秒")
print(f"平均单次查询: {search_time/nq*1000:.2f}ms")
print(f"索引占用的内存（估算）: {index_pq.ntotal * m * nbits / 8 / 1024 / 1024:.2f} MB")

# 对比：纯内存占用
flat_index = faiss.IndexFlatL2(d)
flat_index.add(xb)
flat_size = nb * d * 4 / 1024 / 1024  # float32
print(f"Flat索引内存占用（估算）: {flat_size:.2f} MB")
print(f"压缩比: {flat_size / (index_pq.ntotal * m * nbits / 8 / 1024 / 1024):.1f}x")
