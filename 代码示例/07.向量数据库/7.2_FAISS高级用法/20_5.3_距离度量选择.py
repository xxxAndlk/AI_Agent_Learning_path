import faiss
import numpy as np

def compare_metrics():
    """对比不同距离度量"""
    d = 128
    n = 10000
    
    np.random.seed(42)
    xb = np.random.random((n, d)).astype('float32')
    xq = np.random.random((5, d)).astype('float32')
    
    # L2距离索引
    index_l2 = faiss.IndexFlatL2(d)
    index_l2.add(xb)
    D_l2, I_l2 = index_l2.search(xq, k=3)
    
    # 内积索引（需要归一化向量）
    xb_norm = xb / np.linalg.norm(xb, axis=1, keepdims=True)
    xq_norm = xq / np.linalg.norm(xq, axis=1, keepdims=True)
    
    index_ip = faiss.IndexFlatIP(d)
    index_ip.add(xb_norm)
    D_ip, I_ip = index_ip.search(xq_norm, k=3)
    
    print("=== L2距离 vs 内积（归一化后等价于余弦相似度）===\n")
    print("L2距离结果（越小越相似）:")
    print(D_l2)
    
    print("\n内积结果（越大越相似）:")
    print(D_ip)
    
    # 验证等价性
    print("\n验证：归一化后的L2距离与内积的关系")
    for i in range(3):
        # 使用L2距离计算
        l2_dist = D_l2[0, i]
        # 转换为余弦相似度
        cosine_sim = 1 - l2_dist**2 / 2
        # 内积
        ip_val = D_ip[0, i]
        print(f"  结果{i}: L2={l2_dist:.3f}, cos_sim≈{cosine_sim:.3f}, IP={ip_val:.3f}")

compare_metrics()
