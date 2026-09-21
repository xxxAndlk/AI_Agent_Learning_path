import faiss
import numpy as np
import matplotlib.pyplot as plt

def visualize_pq():
    """可视化PQ原理"""
    # 假设二维向量，分割为2个子向量
    # 每个子向量独立量化
    
    d = 2
    m = 2  # 2个子向量
    nbits = 2  # 每个码字2位（4个码字）
    
    # 生成一些测试向量
    np.random.seed(42)
    vectors = np.random.random((100, d)) * 10
    
    # 分隔点
    split = d // m  # 1
    
    # 子向量1
    subvec1 = vectors[:, :split]
    # 子向量2
    subvec2 = vectors[:, split:]
    
    # 训练独立量化器
    codebook1 = faiss.IndexFlatL2(split)
    codebook1.train(subvec1)
    
    codebook2 = faiss.IndexFlatL2(split)
    codebook2.train(subvec2)
    
    print("原始向量维度:", d)
    print("子向量数:", m)
    print("每个子向量码字数:", 2**nbits)
    print("每个向量编码长度:", m * nbits, "bits")
    print("压缩比:", d * 32 / (m * nbits), "倍")
    
visualize_pq()
