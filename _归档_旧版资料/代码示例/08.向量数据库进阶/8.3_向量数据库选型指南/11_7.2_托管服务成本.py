def calculate_managed_cost(vector_count: int, qps: int) -> dict:
    """
    计算托管服务成本（估算）
    """
    # Pinecone定价（简化估算）
    # Serverless按请求计费，Standard按容量计费
    
    # 存储成本
    storage_cost = vector_count * 512 / 1024 / 1024 * 0.25  # ~$0.25/GB
    
    # 请求成本（假设每次搜索消耗1个单元）
    monthly_requests = qps * 3600 * 24 * 30
    request_cost = monthly_requests * 0.0004  # ~$0.0004/单元
    
    total = storage_cost + request_cost
    
    return {
        "存储成本": f"${storage_cost:.2f}/月",
        "请求成本": f"${request_cost:.2f}/月",
        "总成本": f"${total:.2f}/月",
        "每向量成本": f"${total/vector_count*10000:.4f}/万向量"
    }

print("\n" + "=" * 60)
print("托管服务（Pinecone）成本估算")
print("=" * 60)

for scale in [10000, 100000, 1000000]:
    qps = scale // 1000
    print(f"\n数据规模: {scale:,} 向量, QPS: {qps}")
    costs = calculate_managed_cost(scale, qps)
    for k, v in costs.items():
        print(f"  {k}: {v}")
