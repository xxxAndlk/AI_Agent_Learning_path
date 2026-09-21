import faiss
import numpy as np
import psutil
import os

def get_memory_usage_mb():
    """获取当前进程内存使用量（MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# ============ HNSW内存优化示例 ============

d = 128
nb = 100000

np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')

print("=" * 60)
print("HNSW内存占用对比")
print("=" * 60)
print(f"原始数据大小: {nb * d * 4 / 1024 / 1024:.2f} MB")
print("-" * 60)

# 测试不同M值的内存占用
for M in [8, 16, 32, 64]:
    mem_before = get_memory_usage_mb()
    index = faiss.IndexHNSWFlat(d, M)
    index.add(xb)
    mem_after = get_memory_usage_mb()
    
    # 获取索引的描述信息（包含内存估算）
    index_size = mem_after - mem_before
    
    print(f"M={M:<4}: 索引内存 ≈ {index_size:.2f} MB")
