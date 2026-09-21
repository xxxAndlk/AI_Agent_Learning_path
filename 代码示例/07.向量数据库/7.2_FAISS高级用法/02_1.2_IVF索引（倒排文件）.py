import faiss
import numpy as np
import time

# 参数设置
d = 128
n = 1000000                 # 100万向量
nlist = 100                 # 聚类中心数量
nprobe = 10                 # 搜索的聚类数量

# 生成数据
np.random.seed(42)
xb = np.random.random((n, d)).astype('float32')

# 创建IVF-Flat索引
# 第一个参数是量化器（用于聚类），这里使用Flat索引作为量化器
# 第二个参数是向量维度
# 第三个参数是聚类数量nlist
quantizer = faiss.IndexFlatL2(d)
index_ivf = faiss.IndexIVFFlat(quantizer, d, nlist)

print("开始训练IVF索引...")
start_time = time.time()
index_ivf.train(xb)          # 训练阶段：确定聚类中心
train_time = time.time() - start_time
print(f"训练耗时: {train_time:.2f} 秒")
print(f"是否训练完成: {index_ivf.is_trained}")

# 添加向量
print("开始添加向量...")
start_time = time.time()
index_ivf.add(xb)
add_time = time.time() - start_time
print(f"添加 {n} 向量耗时: {add_time:.2f} 秒")

# 搜索性能测试
nq = 100
xq = np.random.random((nq, d)).astype('float32')

# 测试不同nprobe值的影响
for probe in [1, 5, 10, 20, 50]:
    index_ivf.nprobe = probe
    start_time = time.time()
    D, I = index_ivf.search(xq, k=10)
    search_time = time.time() - start_time
    
    # 计算召回率（与Flat索引对比）
    index_flat = faiss.IndexFlatL2(d)
    index_flat.add(xb[:10000])  # 用小数据集对比
    D_ref, I_ref = index_flat.search(xq, k=10)
    
    # 简单计算召回率
    recall = np.mean([len(set(I[i]) & set(I_ref[i]))/10 for i in range(nq)])
    
    print(f"nprobe={probe:2d}: 耗时 {search_time:.3f}s, "
          f"QPS={nq/search_time:.1f}, 召回率≈{recall:.2%}")
