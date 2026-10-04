# 不同索引类型的性能对比
print("\n" + "=" * 80)
print("索引类型性能对比（100K向量，128维）")
print("=" * 80)
print(f"{'索引类型':<20} {'构建时间':<15} {'搜索延迟':<15} {'内存(MB)':<15} {'召回率':<10}")
print("-" * 80)

index_results = [
    ("Flat (L2)", "0.5s", "52ms", "48", "100%"),
    ("IVF-Flat", "3.2s", "8ms", "52", "99%"),
    ("IVF-PQ", "4.1s", "2ms", "18", "97%"),
    ("HNSW", "8.5s", "2ms", "65", "98%"),
    ("Annoy", "6.2s", "3ms", "42", "96%"),
]

for result in index_results:
    print(f"{result[0]:<20} {result[1]:<15} {result[2]:<15} {result[3]:<15} {result[4]:<10}")
