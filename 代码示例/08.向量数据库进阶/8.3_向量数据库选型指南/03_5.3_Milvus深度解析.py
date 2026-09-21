import numpy as np

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# 连接Milvus
connections.connect(host="localhost", port="19530")

# 定义schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=50)
]
schema = CollectionSchema(fields=fields, description="文档集合")

# 创建集合
collection = Collection(name="documents", schema=schema)

# 创建索引
index_params = {
    "index_type": "HNSW",
    "metric_type": "L2",
    "params": {"M": 32, "efConstruction": 128}
}
collection.create_index(field_name="vector", index_params=index_params)

# 插入数据
data = [
    [1, 2, 3],  # id
    [[np.random.rand(128).tolist()] for _ in range(3)],  # vector
    ["文本1", "文本2", "文本3"],  # text
    ["tech", "science", "tech"]  # category
]
collection.insert(data)

# 搜索
search_params = {"metric_type": "L2", "params": {"ef": 64}}
query_vector = [np.random.rand(128).tolist()]
results = collection.search(
    data=query_vector,
    anns_field="vector",
    param=search_params,
    limit=10,
    expr='category == "tech"'
)

print(f"找到 {len(results[0])} 个结果")
