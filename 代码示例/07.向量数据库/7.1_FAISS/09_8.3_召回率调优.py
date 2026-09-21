import faiss
import numpy as np

# ============ IVF召回率调优示例 ============

d = 128
nb = 50000
nq = 100
k = 10

# 生成测试数据
np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

# 创建基准索引（Flat，用于计算真实最近邻）
index_flat = faiss.IndexFlatL2(d)
index_flat.add(xb)
D_flat, I_flat = index_flat.search(xq, k)

# 创建IVF索引
quantizer = faiss.IndexFlatL2(d)
nlist = 100
index_ivf = faiss.IndexIVFFlat(quantizer, d, nlist)
index_ivf.train(xb)
index_ivf.add(xb)

print("=" * 60)
print("nprobe参数与召回率关系")
print("=" * 60)
print(f"{'nprobe':<10} {'耗时(ms)':<15} {'召回率':<15}")
print("-" * 40)

for nprobe in [1, 2, 5, 10, 20, 50, 100]:
    index_ivf.nprobe = nprobe
    
    start = time.time()
    D_ivf, I_ivf = index_ivf.search(xq, k)
    elapsed = time.time() - start
    
    # 计算召回率
    recall = 0
    for i in range(nq):
        true_set = set(I_flat[i])
        result_set = set(I_ivf[i])
        recall += len(true_set & result_set) / k
    recall /= nq
    
    print(f"{nprobe:<10} {elapsed*1000/nq:<15.2f} {recall*100:<15.2f}%")
