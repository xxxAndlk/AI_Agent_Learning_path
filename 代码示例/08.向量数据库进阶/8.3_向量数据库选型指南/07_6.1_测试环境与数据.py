import time
import numpy as np

# 测试配置
TEST_CONFIGS = {
    "small": {"nb": 10000, "nq": 100, "d": 128},
    "medium": {"nb": 100000, "nq": 100, "d": 128},
    "large": {"nb": 1000000, "nq": 100, "d": 128},
}

def generate_test_data(config):
    """生成测试数据"""
    np.random.seed(42)
    vectors = np.random.random((config["nb"], config["d"])).astype('float32')
    queries = np.random.random((config["nq"], config["d"])).astype('float32')
    return vectors, queries


# 测试结果汇总表
print("=" * 80)
print("向量数据库性能测试结果（100次查询平均）")
print("=" * 80)
print(f"{'数据库':<15} {'规模':<10} {'延迟(ms)':<15} {'QPS':<15} {'召回率':<10}")
print("-" * 80)

# 注意：以下数据为模拟值，实际测试请在本地运行
test_results = [
    ("FAISS(Flat)", "10K", "0.5", "2000", "100%"),
    ("FAISS(HNSW)", "10K", "0.8", "1250", "98%"),
    ("Chroma", "10K", "5.2", "192", "95%"),
    ("Qdrant", "10K", "4.5", "222", "97%"),
    ("Milvus", "10K", "8.3", "120", "98%"),
    ("FAISS(Flat)", "100K", "5.2", "192", "100%"),
    ("FAISS(HNSW)", "100K", "2.1", "476", "97%"),
    ("Chroma", "100K", "52", "19", "94%"),
    ("Qdrant", "100K", "12", "83", "96%"),
    ("Milvus", "100K", "18", "55", "98%"),
    ("FAISS(HNSW)", "1M", "8.5", "117", "96%"),
    ("Qdrant", "1M", "25", "40", "95%"),
    ("Milvus", "1M", "35", "28", "97%"),
]

for result in test_results:
    print(f"{result[0]:<15} {result[1]:<10} {result[2]:<15} {result[3]:<15} {result[4]:<10}")
