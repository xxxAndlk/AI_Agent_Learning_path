def calculate_self_hosted_cost(vector_count: int, qps: int) -> dict:
    """
    计算自托管方案成本（估算）
    
    参数:
        vector_count: 向量数量
        qps: 每秒查询数
    """
    # 估算内存需求（按每向量0.5KB计算）
    memory_gb = vector_count * 512 / 1024 / 1024
    memory_cost = memory_gb * 15  # 每GB内存约15美元/月
    
    # CPU需求估算
    cpu_cores = max(4, qps // 100)
    cpu_cost = cpu_cores * 20  # 每核约20美元/月
    
    # 存储（按向量1KB计算）
    storage_gb = vector_count * 1024 / 1024 / 1024
    storage_cost = storage_gb * 0.1  # 每GB约0.1美元/月
    
    # 云服务器基础费用
    server_cost = 100  # 基础服务器约100美元/月
    
    total = memory_cost + cpu_cost + storage_cost + server_cost
    
    return {
        "内存成本": f"${memory_cost:.0f}/月",
        "CPU成本": f"${cpu_cost:.0f}/月",
        "存储成本": f"${storage_cost:.0f}/月",
        "服务器成本": f"${server_cost:.0f}/月",
        "总成本": f"${total:.0f}/月"
    }

# 示例计算
for scale in [10000, 100000, 1000000, 10000000]:
    qps = scale // 1000
    print(f"\n数据规模: {scale:,} 向量, QPS: {qps}")
    costs = calculate_self_hosted_cost(scale, qps)
    for k, v in costs.items():
        print(f"  {k}: {v}")
