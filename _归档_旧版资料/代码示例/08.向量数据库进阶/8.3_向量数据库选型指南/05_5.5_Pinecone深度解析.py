import numpy as np

from pinecone import Pinecone

# 初始化（使用API Key）
pc = Pinecone(api_key="your-api-key")

# 创建索引
pc.create_index(
    name="documents",
    dimension=128,
    metric="cosine",
    spec={
        "serverless": {
            "cloud": "aws",
            "region": "us-west-2"
        }
    }
)

# 连接索引
index = pc.Index("documents")

# 添加向量
vectors = [
    {
        "id": f"vec{i}",
        "values": np.random.rand(128).tolist(),
        "metadata": {"text": f"文档{i}"}
    }
    for i in range(1000)
]

index.upsert(vectors=vectors)

# 搜索
query_vector = np.random.rand(128).tolist()
results = index.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True
)

for match in results["matches"]:
    print(f"ID: {match['id']}, Score: {match['score']}")
