# 批量查询性能对比
print("\n" + "=" * 80)
print("批量查询性能对比（1000个查询）")
print("=" * 80)
print(f"{'数据库':<15} {'批量耗时':<15} {'平均延迟':<15} {'QPS':<15}")
print("-" * 80)

batch_results = [
    ("FAISS", "52ms", "0.05ms", "19230"),
    ("Qdrant", "120ms", "0.12ms", "8333"),
    ("Milvus", "180ms", "0.18ms", "5555"),
    ("Pinecone", "250ms", "0.25ms", "4000"),
]

for result in batch_results:
    print(f"{result[0]:<15} {result[1]:<15} {result[2]:<15} {result[3]:<15}")
