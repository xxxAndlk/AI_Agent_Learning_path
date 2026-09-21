import faiss
import numpy as np
import time

def tune_hnsw_params():
    """调优HNSW参数"""
    d = 128
    n = 500000
    
    np.random.seed(42)
    xb = np.random.random((n, d)).astype('float32')
    xq = np.random.random((100, d)).astype('float32')
    
    # 参考结果
    index_ref = faiss.IndexFlatL2(d)
    index_ref.add(xb)
    D_ref, I_ref = index_ref.search(xq, k=10)
    
    print("=== M参数调优（efSearch=64）===\n")
    
    results_M = []
    for M in [8, 16, 32, 64]:
        index = faiss.IndexHNSWFlat(d, M)
        index.hnsw.efSearch = 64
        index.add(xb)
        
        start = time.time()
        D, I = index.search(xq, k=10)
        search_time = time.time() - start
        
        recall = np.mean([
            len(set(I[i]) & set(I_ref[i])) / 10 
            for i in range(100)
        ])
        
        # 估算内存
        # 约等于 n * (d + M * 4) * 4 bytes
        memory_mb = n * (d + M * 4) * 4 / 1024 / 1024
        
        results_M.append({
            'M': M,
            'recall': recall,
            'search_time': search_time / 100 * 1000,
            'memory_mb': memory_mb
        })
    
    print(f"{'M':>4} {'召回率':>10} {'搜索时间(ms)':>14} {'内存(MB)':>12}")
    print("-" * 44)
    for r in results_M:
        print(f"{r['M']:>4} {r['recall']:>9.2%} "
              f"{r['search_time']:>13.2f} {r['memory_mb']:>11.1f}")
    
    print("\n=== efSearch参数调优（M=32）===\n")
    
    index = faiss.IndexHNSWFlat(d, 32)
    index.add(xb)
    
    results_ef = []
    for ef in [8, 16, 32, 64, 128, 256]:
        index.hnsw.efSearch = ef
        start = time.time()
        D, I = index.search(xq, k=10)
        search_time = time.time() - start
        
        recall = np.mean([
            len(set(I[i]) & set(I_ref[i])) / 10 
            for i in range(100)
        ])
        
        results_ef.append({
            'efSearch': ef,
            'recall': recall,
            'search_time': search_time / 100 * 1000
        })
    
    print(f"{'efSearch':>10} {'召回率':>10} {'搜索时间(ms)':>14}")
    print("-" * 37)
    for r in results_ef:
        print(f"{r['efSearch']:>10} {r['recall']:>9.2%} {r['search_time']:>13.2f}")

tune_hnsw_params()
