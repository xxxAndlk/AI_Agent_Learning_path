import faiss
import numpy as np
import time
import matplotlib.pyplot as plt

def tune_ivf_params():
    """调优IVF参数"""
    d = 128
    n = 500000
    
    np.random.seed(42)
    xb = np.random.random((n, d)).astype('float32')
    xq = np.random.random((100, d)).astype('float32')
    
    # 参考结果
    index_ref = faiss.IndexFlatL2(d)
    index_ref.add(xb)
    D_ref, I_ref = index_ref.search(xq, k=10)
    
    print("=== nlist参数调优 ===\n")
    
    # 测试不同nlist
    results_nlist = []
    for nlist in [50, 100, 200, 500, 1000]:
        quantizer = faiss.IndexFlatL2(d)
        index = faiss.IndexIVFFlat(quantizer, d, nlist)
        index.train(xb)
        index.add(xb)
        
        for nprobe in [10]:
            index.nprobe = nprobe
            start = time.time()
            D, I = index.search(xq, k=10)
            search_time = time.time() - start
            
            recall = np.mean([
                len(set(I[i]) & set(I_ref[i])) / 10 
                for i in range(100)
            ])
            
            results_nlist.append({
                'nlist': nlist,
                'nprobe': nprobe,
                'recall': recall,
                'search_time': search_time / 100 * 1000
            })
    
    print(f"{'nlist':>6} {'nprobe':>8} {'召回率':>10} {'搜索时间(ms)':>14}")
    print("-" * 42)
    for r in results_nlist:
        print(f"{r['nlist']:>6} {r['nprobe']:>8} "
              f"{r['recall']:>9.2%} {r['search_time']:>13.2f}")
    
    print("\n=== nprobe参数调优 ===\n")
    
    # 测试不同nprobe
    nlist = 200
    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFFlat(quantizer, d, nlist)
    index.train(xb)
    index.add(xb)
    
    results_nprobe = []
    for nprobe in [1, 2, 5, 10, 20, 50, 100]:
        index.nprobe = nprobe
        start = time.time()
        D, I = index.search(xq, k=10)
        search_time = time.time() - start
        
        recall = np.mean([
            len(set(I[i]) & set(I_ref[i])) / 10 
            for i in range(100)
        ])
        
        results_nprobe.append({
            'nprobe': nprobe,
            'recall': recall,
            'search_time': search_time / 100 * 1000
        })
    
    print(f"{'nprobe':>8} {'召回率':>10} {'搜索时间(ms)':>14}")
    print("-" * 35)
    for r in results_nprobe:
        print(f"{r['nprobe']:>8} {r['recall']:>9.2%} {r['search_time']:>13.2f}")

tune_ivf_params()
