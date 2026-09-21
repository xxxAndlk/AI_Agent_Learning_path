import faiss
import numpy as np
import time

def compare_pq_vs_opq():
    """对比PQ和OPQ"""
    d = 128
    n = 100000
    nq = 100
    
    np.random.seed(42)
    xb = np.random.random((n, d)).astype('float32')
    xq = np.random.random((nq, d)).astype('float32')
    
    # 参考索引
    index_ref = faiss.IndexFlatL2(d)
    index_ref.add(xb)
    D_ref, I_ref = index_ref.search(xq, k=10)
    
    # PQ索引
    index_pq = faiss.IndexPQ(d, 8, 8)
    index_pq.train(xb)
    index_pq.add(xb)
    D_pq, I_pq = index_pq.search(xq, k=10)
    
    recall_pq = np.mean([
        len(set(I_pq[i]) & set(I_ref[i])) / 10 
        for i in range(nq)
    ])
    
    # OPQ索引
    index_opq = faiss.IndexOPQ(d, 8, 8)
    index_opq.train(xb)
    index_opq.add(xb)
    D_opq, I_opq = index_opq.search(xq, k=10)
    
    recall_opq = np.mean([
        len(set(I_opq[i]) & set(I_ref[i])) / 10 
        for i in range(nq)
    ])
    
    print(f"PQ召回率: {recall_pq:.2%}")
    print(f"OPQ召回率: {recall_opq:.2%}")
    print(f"OPQ提升: {(recall_opq - recall_pq):.2%}")

compare_pq_vs_opq()
