def collection_management():
    """集合管理操作"""
    
    client = chromadb.PersistentClient(
        path="./chroma_data"
    )
    
    # 1. 创建集合
    collection = client.create_collection(
        name="my_collection",
        metadata={"description": "我的知识库"}  # 集合级别的元数据
    )
    
    # 2. 获取已存在的集合
    existing_collection = client.get_collection(name="my_collection")
    
    # 3. 获取或创建集合（如果不存在则创建）
    safe_collection = client.get_or_create_collection(
        name="safe_collection",
        metadata={"created_by": "system"}
    )
    
    # 4. 列出所有集合
    all_collections = client.list_collections()
    print("所有集合:")
    for col in all_collections:
        print(f"  - {col.name}: {col.count()} 文档")
    
    # 5. 删除集合
    # client.delete_collection(name="old_collection")
    
    # 6. 修改集合元数据
    collection = client.get_collection(name="my_collection")
    collection.modify(metadata={"updated": "true", "version": "2.0"})
    
    # 7. 集合的其他操作
    print(f"文档数量: {collection.count()}")
    print(f"集合名称: {collection.name}")
    print(f"集合元数据: {collection.metadata}")


def collection_operations():
    """集合的增删改查操作"""
    
    client = chromadb.PersistentClient(
        path="./chroma_advanced"
    )
    
    collection = client.get_or_create_collection(
        name="advanced_demo"
    )
    
    # ============ 添加文档 ============
    # 方式1：直接添加文档（自动生成嵌入）
    collection.add(
        documents=[
            "Python是一种高级编程语言",
            "JavaScript是Web前端开发语言",
            "Java是企业级应用开发语言"
        ],
        ids=["doc1", "doc2", "doc3"],
        metadatas=[
            {"language": "Python", "type": "programming"},
            {"language": "JavaScript", "type": "programming"},
            {"language": "Java", "type": "programming"}
        ]
    )
    
    # 方式2：添加预计算的向量
    import numpy as np
    
    # 手动创建向量（768维，例如bge系列开源embedding模型）
    vectors = [
        np.random.rand(768).tolist(),
        np.random.rand(768).tolist(),
        np.random.rand(768).tolist()
    ]
    
    collection.add(
        ids=["vec1", "vec2", "vec3"],
        embeddings=vectors,
        documents=["文档A", "文档B", "文档C"]
    )
    
    # 方式3：批量添加大量文档
    bulk_documents = [f"文档{i}" for i in range(100)]
    bulk_ids = [f"bulk_doc_{i}" for i in range(100)]
    bulk_metadatas = [{"index": i, "batch": "bulk"} for i in range(100)]
    
    collection.add(
        documents=bulk_documents,
        ids=bulk_ids,
        metadatas=bulk_metadatas
    )
    
    print(f"添加后文档总数: {collection.count()}")
    
    # ============ 查询文档 ============
    results = collection.query(
        query_texts=["Python编程"],
        n_results=5,
        include=["documents", "distances", "metadatas"]
    )
    
    # ============ 更新文档 ============
    collection.update(
        ids=["doc1"],
        documents=["Python是一种强大的人工智能编程语言"],
        metadatas=[{"language": "Python", "type": "AI"}]
    )
    
    # ============ 删除文档 ============
    collection.delete(ids=["doc1", "doc2"])
    
    # ============ 获取文档 ============
    # 获取指定ID的文档
    get_result = collection.get(ids=["doc3"])
    print("获取的文档:", get_result)


# 运行集合操作示例
collection_operations()
