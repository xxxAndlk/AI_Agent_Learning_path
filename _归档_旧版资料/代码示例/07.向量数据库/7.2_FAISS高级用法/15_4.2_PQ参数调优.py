import faiss
import numpy as np
import time

def optimize_pq_params(d, n, nq=100):
    """寻找最优PQ参数"""
    np.random.seed(42)
    xb = np.random.random((n, d)).astype('float32')
    xq = np.random.random((nq, d)).astype('float32')
    
    # 真实最近邻（用于计算召回率）
    index_ref = faiss.IndexFlatL2(d)
    index_ref.add(xb)
    D_ref, I_ref = index_ref.search(xq, k=10)
    
    results = []
    
    # 测试不同参数组合
    for m in [4, 8, 16, 32]:
        for nbits in [8, 12, 16]:
            index = faiss.IndexPQ(d, m, nbits)
            
            start = time.time()
            index.train(xb)
            train_time = time.time() - start
            
            start = time.time()
            index.add(xb)
            add_time = time.time() - start
            
            start = time.time()
            D, I = index.search(xq, k=10)
            search_time = time.time() - start
            
            # 计算召回率
            recall = np.mean([
                len(set(I[i]) & set(I_ref[i])) / 10 
                for i in range(nq)
            ])
            
            # 计算存储大小
            storage_ratio = (d * 4) / (m * nbits / 8)
            
            results.append({
                'm': m,
                'nbits': nbits,
                'recall': recall,
                'search_time_ms': search_time / nq * 1000,
                'storage_ratio': storage_ratio,
                'train_time': train_time
            })
            
    # 打印结果
    print("\n=== PQ参数对比 ===")
    print(f"{'m':>4} {'nbits':>6} {'召回率':>8} {'搜索ms':>10} {'压缩比':>10}")
    print("-" * 45)
    for r in sorted(results, key=lambda x: -x['recall']):
        print(f"{r['m']:>4} {r['nbits']:>6} {r['recall']:>7.2%} "
              f"{r['search_time_ms']:>9.2f} {r['storage_ratio']:>9.1f}x")

# 测试
optimize_pq_params(d=128, n=100000)
