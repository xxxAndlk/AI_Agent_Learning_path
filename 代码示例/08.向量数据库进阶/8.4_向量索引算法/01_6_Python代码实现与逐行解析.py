import faiss
import numpy as np
from typing import List, Tuple
import time

def hnsw_example():
    """HNSW索引示例
    
    HNSW (Hierarchical Navigable Small World) 是目前最先进的ANN算法之一
    适合大规模、高召回率的场景
    """
    print("=" * 60)
    print("HNSW索引示例")
    print("=" * 60)
    
    # 参数设置
    d = 128                             # 向量维度
    nb = 100000                         # 数据库向量数量
    nq = 1000                           # 查询向量数量
    k = 10                              # 返回最近邻数量
    
    print(f"\n数据集参数:")
    print(f"  维度: {d}")
    print(f"  数据库大小: {nb}")
    print(f"  查询数量: {nq}")
    print(f"  返回Top-K: {k}")
    
    # 生成随机数据
    np.random.seed(42)
    xb = np.random.random((nb, d)).astype('float32')
    xq = np.random.random((nq, d)).astype('float32')
    
    # 归一化向量（用于余弦相似度）
    faiss.normalize_L2(xb)
    faiss.normalize_L2(xq)
    
    # ============ 创建HNSW索引 ============
    print("\n--- 创建HNSW索引 ---")
    
    # HNSW参数
    M = 16                              # 每个节点的连接数，越大召回率越高，内存占用越大
    efConstruction = 200                # 构建时的搜索范围，越大构建越慢，质量越好
    
    # 创建索引
    # IndexHNSWFlat: 使用Flat存储的HNSW索引
    index = faiss.IndexHNSWFlat(d, M)
    index.hnsw.efConstruction = efConstruction
    
    print(f"HNSW参数:")
    print(f"  M (连接数): {M}")
    print(f"  efConstruction (构建搜索范围): {efConstruction}")
    
    # 添加向量
    print("\n添加向量到索引...")
    start_time = time.time()
    index.add(xb)
    build_time = time.time() - start_time
    print(f"✅ 索引构建完成，耗时: {build_time:.2f}秒")
    print(f"  索引大小: {nb} 个向量")
    
    # ============ 搜索 ============
    print("\n--- 执行搜索 ---")
    
    # 设置搜索参数
    efSearch = 64                       # 搜索时的候选集大小，越大召回率越高，速度越慢
    index.hnsw.efSearch = efSearch
    
    print(f"搜索参数 efSearch: {efSearch}")
    
    # 执行搜索
    start_time = time.time()
    D, I = index.search(xq, k)
    search_time = time.time() - start_time
    
    print(f"\n搜索结果:")
    print(f"  查询次数: {nq}")
    print(f"  总耗时: {search_time:.4f}秒")
    print(f"  平均单次查询: {(search_time/nq)*1000:.2f}ms")
    print(f"  QPS: {nq/search_time:.1f}")
    
    print(f"\n查询示例 (前3个):")
    for i in range(min(3, nq)):
        print(f"  查询{i}: 最近邻索引 {I[i][:5]}, 距离 {D[i][:5]}")
    
    # ============ 与暴力搜索对比 ============
    print("\n--- 精度验证 (与暴力搜索对比) ---")
    
    # 创建Flat索引作为基准
    index_flat = faiss.IndexFlatIP(d)   # 内积距离（归一化后等价于余弦相似度）
    index_flat.add(xb)
    
    # 暴力搜索
    D_gt, I_gt = index_flat.search(xq, k)
    
    # 计算召回率
    recalls = []
    for i in range(nq):
        # 计算HNSW结果中有多少在真实Top-K中
        correct = len(set(I[i]) & set(I_gt[i]))
        recalls.append(correct / k)
    
    avg_recall = np.mean(recalls)
    print(f"召回率 (Recall@{k}): {avg_recall*100:.2f}%")
    print(f"  平均每个查询找到 {avg_recall*k:.1f}/{k} 个真实最近邻")
    
    # ============ 参数调优演示 ============
    print("\n--- efSearch参数影响 ---")
    ef_values = [16, 32, 64, 128, 256]
    
    print(f"{'efSearch':<10} {'Recall@10':<12} {'Query Time(ms)':<15} {'QPS':<10}")
    print("-" * 50)
    
    for ef in ef_values:
        index.hnsw.efSearch = ef
        
        # 搜索
        start = time.time()
        D_test, I_test = index.search(xq, k)
        elapsed = time.time() - start
        
        # 计算召回率
        recalls_test = [len(set(I_test[i]) & set(I_gt[i])) / k for i in range(nq)]
        recall = np.mean(recalls_test)
        
        print(f"{ef:<10} {recall*100:>6.2f}%      {(elapsed/nq)*1000:>6.2f}          {nq/elapsed:>6.1f}")


def hnsw_memory_usage():
    """分析HNSW内存占用"""
    print("\n" + "=" * 60)
    print("HNSW内存占用分析")
    print("=" * 60)
    
    d = 128
    nb = 100000
    M_values = [8, 16, 32, 64]
    
    print(f"\n向量维度: {d}, 向量数量: {nb}")
    print(f"\n{'M':<5} {'内存占用(MB)':<15} {'每向量(bytes)':<15}")
    print("-" * 40)
    
    for M in M_values:
        index = faiss.IndexHNSWFlat(d, M)
        
        # 生成数据并添加
        xb = np.random.random((nb, d)).astype('float32')
        index.add(xb)
        
        # 估算内存（简化计算）
        # 原始向量 + HNSW图结构
        vector_memory = nb * d * 4  # float32 = 4 bytes
        graph_memory = nb * M * 2 * 4  # 每个连接存储邻居ID（int32）
        total_memory = (vector_memory + graph_memory) / (1024 * 1024)
        
        bytes_per_vector = (vector_memory + graph_memory) / nb
        
        print(f"{M:<5} {total_memory:>8.2f}        {bytes_per_vector:>8.1f}")
    
    print("\n注意:")
    print("  - M越大，召回率越高，但内存占用越大")
    print("  - M=16是常用的平衡点")


if __name__ == "__main__":
    hnsw_example()
    hnsw_memory_usage()
