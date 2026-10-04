import weaviate
import json

# 连接Weaviate
client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-OpenAI-Api-Key": "your-openai-key"
    }
)

# 定义schema
schema = {
    "class": "Article",
    "vectorizer": "text2vec-transformers",
    "moduleConfig": {
        "text2vec-transformers": {
            "vectorizeClassName": False
        }
    },
    "properties": [
        {"name": "title", "dataType": ["text"]},
        {"name": "content", "dataType": ["text"]},
        {"name": "category", "dataType": ["text"]}
    ]
}

client.schema.create_class(schema)

# 添加数据
client.data_object.create(
    class_name="Article",
    data_object={
        "title": "机器学习入门",
        "content": "机器学习是人工智能的一个分支...",
        "category": "tech"
    }
)

# 搜索（使用nearText）
response = client.query.get(
    "Article",
    ["title", "content", "category"]
).with_near_text({
    "concepts": ["深度学习"]
}).with_limit(5).do()

print(json.dumps(response, indent=2))
