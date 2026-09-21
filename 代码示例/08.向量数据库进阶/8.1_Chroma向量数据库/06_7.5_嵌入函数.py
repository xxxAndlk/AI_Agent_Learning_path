"""
Chroma支持多种嵌入函数：
1. sentence-transformers (默认)
2. OpenAI Embeddings
3. Cohere Embeddings
4. Hugging Face Embeddings
5. 自定义嵌入函数
"""

def embedding_functions():
    """嵌入函数详解"""
    
    import chromadb
    from chromadb.embeddings import SentenceTransformerEmbeddingFunction
    
    client = chromadb.PersistentClient(
        path="./embedding_demo"
    )
    
    # ============ 方式1: 使用默认的sentence-transformers ============
    # 自动使用 all-MiniLM-L6-v2 模型
    collection1 = client.create_collection(
        name="default_embeddings",
        embedding_function=SentenceTransformerEmbeddingFunction()
    )
    
    # ============ 方式2: 指定模型 ============
    collection2 = client.create_collection(
        name="custom_model",
        embedding_function=SentenceTransformerEmbeddingFunction(
            model_name="multi-qa-MiniLM-L6-cos-v1"  # 专用检索模型
        )
    )
    
    # ============ 方式3: 使用OpenAI Embeddings ============
    # 需要安装 openai 包并设置API密钥
    try:
        from chromadb.embeddings import OpenAIEmbeddingFunction
        
        # 设置API密钥
        import os
        os.environ["OPENAI_API_KEY"] = "your-api-key"
        
        collection3 = client.create_collection(
            name="openai_embeddings",
            embedding_function=OpenAIEmbeddingFunction(
                model="text-embedding-3-small"
            )
        )
    except ImportError:
        print("请安装openai: pip install openai")
    
    # ============ 方式4: 使用Cohere Embeddings ============
    try:
        from chromadb.embeddings import CohereEmbeddingFunction
        
        collection4 = client.create_collection(
            name="cohere_embeddings",
            embedding_function=CohereEmbeddingFunction(
                model="embed-multilingual-v3.0",
                api_key="your-cohere-key"
            )
        )
    except ImportError:
        print("请安装cohere: pip install cohere")
    
    # 添加文档测试
    test_docs = ["人工智能改变世界", "深度学习是AI的核心技术"]
    
    for collection in [collection1, collection2]:
        collection.add(
            documents=test_docs,
            ids=["d1", "d2"]
        )
        
        results = collection.query(
            query_texts=["机器学习和AI"],
            n_results=1
        )
        print(f"集合 {collection.name} 结果:", results['documents'])
    
    return client


def custom_embedding_function():
    """自定义嵌入函数"""
    
    import chromadb
    from chromadb.embeddings import EmbeddingFunction
    import numpy as np
    from typing import List
    
    class MyCustomEmbeddings(EmbeddingFunction):
        """自定义嵌入函数示例"""
        
        def __init__(self, dimension: int = 128):
            self.dimension = dimension
        
        def __call__(self, texts: List[str]) -> List[List[float]]:
            """
            将文本转换为向量
            
            这里使用简单的随机向量作为示例
            实际应用中应该使用真实的嵌入模型
            """
            embeddings = []
            for text in texts:
                # 生成伪随机向量（实际应使用真实的嵌入模型）
                np.random.seed(hash(text) % (2**32))
                embedding = np.random.rand(self.dimension).tolist()
                embeddings.append(embedding)
            return embeddings
    
    # 使用自定义嵌入函数
    client = chromadb.PersistentClient(
        path="./custom_embedding"
    )
    
    collection = client.create_collection(
        name="custom_emb",
        embedding_function=MyCustomEmbeddings(dimension=256)
    )
    
    # 添加文档
    collection.add(
        documents=["第一个文档", "第二个文档"],
        ids=["d1", "d2"]
    )
    
    # 查询
    results = collection.query(
        query_texts=["第一个"],
        n_results=1
    )
    print("自定义嵌入结果:", results['documents'])


# 运行嵌入函数示例
embedding_functions()
custom_embedding_function()
