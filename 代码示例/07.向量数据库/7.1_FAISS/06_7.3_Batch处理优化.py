import faiss
import numpy as np
import time

# ============ 批量搜索优化示例 ============

d = 128
nb = 50000
nq_list = [1, 10, 100, 1000]
k = 10

# 创建索引并添加数据
np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')
index = faiss.IndexFlatL2(d)
index.add(xb)

print("=" * 60)
print("批量搜索性能测试")
print("=" * 60)

for nq in nq_list:
    xq = np.random.random((nq, d)).astype('float32')
    
    # 多次测试取平均
    times = []
    for _ in range(5):
        start = time.time()
        D, I = index.search(xq, k)
        times.append(time.time() - start)
    
    avg_time = np.mean(times)
    qps = nq / avg_time
    
    print(f"查询数: {nq:4d} | "
          f"平均耗时: {avg_time*1000:8.2f}ms | "
          f"QPS: {qps:8.2f}")
