import chromadb

# 创建客户端（嵌入式模式；0.4+用PersistentClient替代Client+Settings写法）
# 纯内存模式可用chromadb.Client()（数据不落盘）
client = chromadb.PersistentClient(path="./chroma_demo")

# 创建集合
collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # 使用余弦距离
)

# 添加文档
collection.add(
    documents=["文档1内容", "文档2内容", "文档3内容"],
    ids=["doc1", "doc2", "doc3"],
    metadatas=[
        {"category": "tech", "source": "blog"},
        {"category": "science", "source": "paper"},
        {"category": "tech", "source": "docs"}
    ]
)

# 搜索
results = collection.query(
    query_texts=["查询内容"],
    n_results=2,
    where={"category": "tech"}  # 元数据过滤
)

print(results)
