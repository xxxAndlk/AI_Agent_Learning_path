import numpy as np

def million_scale_benchmark():
    """百万级向量检索基准测试"""
    
    print("=" * 60)
    print("百万级向量检索性能测试")
    print("=" * 60)
    
    # 配置
    d = 128
    n = 1000000  # 100万向量
    nq = 1000   # 1000次查询
    
    # 生成测试数据
    print("\n生成测试数据...")
    np.random.seed(42)
    xb = np.random.random((n, d)).astype('float32')
    xq = np.random.random((nq, d)).astype('float32')
    
    # 参考结果（用于召回率计算）
    print("计算参考结果...")
    index_ref = faiss.IndexFlatL2(d)
    index_ref.add(xb[:10000])  # 用子集计算
    _, I_ref = index_ref.search(xq, k=10)
    
    def compute_recall(I):
        return np.mean([
            len(set(I[i]) & set(I_ref[i])) / 10 
            for i in range(nq)
        ])
    
    results = []
    
    # 1. Flat索引
    print("\n--- Flat索引 ---")
    config = IndexConfig(dim=d, index_type='flat')
    system = VectorSearchSystem(config)
    system.add(xb)
    
    start = time.time()
    D, I = system.batch_search(xq, k=10)
    elapsed = time.time() - start
    recall = compute_recall(I)
    
    results.append({
        'name': 'Flat',
        'time_ms': elapsed/nq*1000,
        'qps': nq/elapsed,
        'recall': recall
    })
    print(f"  查询时间: {elapsed/nq*1000:.2f} ms/query")
    print(f"  QPS: {nq/elapsed:.1f}")
    
    # 2. IVF索引
    print("\n--- IVF索引 ---")
    config = IndexConfig(dim=d, index_type='ivf', nlist=512, nprobe=20)
    system = VectorSearchSystem(config)
    system.train(xb)
    system.add(xb)
    
    start = time.time()
    D, I = system.batch_search(xq, k=10)
    elapsed = time.time() - start
    recall = compute_recall(I)
    
    results.append({
        'name': 'IVF',
        'time_ms': elapsed/nq*1000,
        'qps': nq/elapsed,
        'recall': recall
    })
    print(f"  查询时间: {elapsed/nq*1000:.2f} ms/query")
    print(f"  QPS: {nq/elapsed:.1f}")
    print(f"  召回率: {recall:.2%}")
    
    # 3. HNSW索引
    print("\n--- HNSW索引 ---")
    config = IndexConfig(dim=d, index_type='hnsw', M=32, efSearch=64)
    system = VectorSearchSystem(config)
    system.add(xb)
    
    start = time.time()
    D, I = system.batch_search(xq, k=10)
    elapsed = time.time() - start
    recall = compute_recall(I)
    
    results.append({
        'name': 'HNSW',
        'time_ms': elapsed/nq*1000,
        'qps': nq/elapsed,
        'recall': recall
    })
    print(f"  查询时间: {elapsed/nq*1000:.2f} ms/query")
    print(f"  QPS: {nq/elapsed:.1f}")
    print(f"  召回率: {recall:.2%}")
    
    # 4. IVF-PQ索引
    print("\n--- IVF-PQ索引 ---")
    config = IndexConfig(
        dim=d, index_type='ivf-pq',
        nlist=256, nprobe=20,
        m=8, nbits=8
    )
    system = VectorSearchSystem(config)
    system.train(xb)
    system.add(xb)
    
    start = time.time()
    D, I = system.batch_search(xq, k=10)
    elapsed = time.time() - start
    recall = compute_recall(I)
    
    results.append({
        'name': 'IVF-PQ',
        'time_ms': elapsed/nq*1000,
        'qps': nq/elapsed,
        'recall': recall
    })
    print(f"  查询时间: {elapsed/nq*1000:.2f} ms/query")
    print(f"  QPS: {nq/elapsed:.1f}")
    print(f"  召回率: {recall:.2%}")
    
    # 打印汇总表格
    print("\n" + "=" * 60)
    print("性能汇总")
    print("=" * 60)
    print(f"{'索引类型':<12} {'查询时间':<12} {'QPS':<12} {'召回率':<12}")
    print("-" * 50)
    for r in results:
        print(f"{r['name']:<12} {r['time_ms']:<11.2f}ms "
              f"{r['qps']:<11.1f} {r['recall']:<11.2%}")

# 运行测试
million_scale_benchmark()
