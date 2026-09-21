import faiss
import numpy as np
import time

# ============ IVF索引完整示例 ============

# 参数配置
d = 128                      # 向量维度
nb = 100000                  # 数据库规模（10万）
nq = 100                     # 查询数量
k = 10                       # 返回top-k
nlist = 100                  # 聚类数量
nprobe = 10                  # 查询的聚类数量

# 生成测试数据
np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

print("=" * 60)
print("IVF索引演示")
print("=" * 60)

# 方法1：使用IVFFlat（精确但内存占用较大）
# 第一步：创建量化器（用于计算聚类中心）
quantizer = faiss.IndexFlatL2(d)

# 第二步：创建IVFFlat索引
# 参数：量化器、维度、聚类数量
index_ivf = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)

print(f"索引创建前训练状态: {index_ivf.is_trained}")

# 第三步：训练索引（建立聚类中心）
# 训练数据应该是数据向量的一个子集，通常使用全部数据
start_time = time.time()
index_ivf.train(xb)
train_time = time.time() - start_time
print(f"训练耗时: {train_time:.2f}秒")
print(f"训练后状态: {index_ivf.is_trained}")

# 第四步：添加向量
start_time = time.time()
index_ivf.add(xb)
add_time = time.time() - start_time
print(f"添加 {index_ivf.ntotal} 个向量耗时: {add_time:.2f}秒")

# 第五步：设置搜索参数
index_ivf.nprobe = nprobe

# 第六步：执行搜索
start_time = time.time()
D, I = index_search(xq, k)
search_time = time.time() - start_time

print(f"\n搜索参数: nlist={nlist}, nprobe={nprobe}")
print(f"搜索耗时: {search_time:.4f}秒")
print(f"平均单次查询: {search_time/nq*1000:.2f}ms")
