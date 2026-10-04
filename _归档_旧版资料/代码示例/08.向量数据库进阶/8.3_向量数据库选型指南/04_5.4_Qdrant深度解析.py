from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np

# 连接Qdrant
client = QdrantClient(host="localhost", port=6333)

# 创建集合
client.recreate_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=128,
        distance=Distance.COSINE
    )
)

# 添加向量
points = []
for i in range(1000):
    points.append(PointStruct(
        id=i,
        vector=np.random.rand(128).tolist(),
        payload={
            "text": f"文档{i}内容",
            "category": "tech" if i % 2 == 0 else "science"
        }
    ))

client.upsert(
    collection_name="documents",
    points=points
)

# 搜索
search_results = client.search(
    collection_name="documents",
    query_vector=np.random.rand(128).tolist(),
    limit=5,
    query_filter={
        "must": [
            {"key": "category", "match": {"value": "tech"}}
        ]
    }
)

for result in search_results:
    print(f"ID: {result.id}, Score: {result.score}")
