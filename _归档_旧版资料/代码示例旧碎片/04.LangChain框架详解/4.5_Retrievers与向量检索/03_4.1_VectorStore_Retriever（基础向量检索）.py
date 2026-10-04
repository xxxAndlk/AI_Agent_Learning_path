# vector_store_retriever.py
# 基础向量检索器示例

import os
from langchain_community.vectorstores import Chroma, FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.retrievers import VectorStoreRetriever

# 设置API密钥（实际使用时使用环境变量）
os.environ["OPENAI_API_KEY"] = "your-api-key"


def create_vectorstore_retriever():
    """
    创建基础向量检索器
    
    VectorStoreRetriever特点：
    - 简单直接，基于向量相似度
    - 适合大多数场景
    - 支持多种向量数据库
    """
    
    # 1. 准备示例文档
    documents = [
        Document(
            page_content="Python是一种高级编程语言，具有易于学习、语法简洁等特点。",
            metadata={"source": "python_intro.txt", "topic": "编程语言"}
        ),
        Document(
            page_content="Python广泛应用于Web开发、数据科学、机器学习等领域。",
            metadata={"source": "python_usage.txt", "topic": "编程语言"}
        ),
        Document(
            page_content="机器学习是人工智能的一个分支，专注于让计算机从数据中学习。",
            metadata={"source": "ml_intro.txt", "topic": "机器学习"}
        ),
        Document(
            page_content="深度学习是机器学习的一个分支，使用神经网络模型。",
            metadata={"source": "dl_intro.txt", "topic": "深度学习"}
        ),
        Document(
            page_content="RAG结合了检索和生成，可以增强大语言模型的能力。",
            metadata={"source": "rag_intro.txt", "topic": "RAG"}
        ),
        Document(
            page_content="LangChain是一个用于构建LLM应用的框架，提供了丰富的工具。",
            metadata={"source": "langchain_intro.txt", "topic": "LangChain"}
        ),
    ]
    
    # 2. 创建Embedding模型
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 3. 创建向量数据库并添加文档
    # 方式一：使用Chroma（适合本地开发）
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="knowledge_base"
    )
    
    # 方式二：使用FAISS（适合大规模数据）
    # vectorstore = FAISS.from_documents(
    #     documents=documents,
    #     embedding=embeddings
    # )
    
    # 4. 创建VectorStoreRetriever
    retriever = VectorStoreRetriever(
        vectorstore=vectorstore,
        search_type="similarity",  # 检索类型：similarity, similarity_score_threshold, mmr
        search_kwargs={
            "k": 3,  # 返回Top-K个结果
            # "score_threshold": 0.7,  # 相似度阈值（similarity_score_threshold模式）
            # "filter": {"topic": "编程语言"}  # 元数据过滤
        }
    )
    
    return retriever, vectorstore


def test_basic_retrieval():
    """测试基础检索功能"""
    retriever, vectorstore = create_vectorstore_retriever()
    
    test_queries = [
        "Python能做什么？",
        "什么是深度学习？",
        "LangChain的用途",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print("=" * 60)
        
        # 同步检索
        results = retriever.invoke(query)
        
        print(f"\n检索到 {len(results)} 个结果:\n")
        for i, doc in enumerate(results, 1):
            content_preview = doc.page_content[:80].replace("\n", " ")
            print(f"  {i}. {content_preview}...")
            print(f"     来源: {doc.metadata.get('source')}")
            print(f"     主题: {doc.metadata.get('topic')}")


def demonstrate_search_types():
    """演示不同的搜索类型"""
    retriever, vectorstore = create_vectorstore_retriever()
    query = "Python机器学习"
    
    print(f"\n查询: {query}\n")
    
    # 1. 相似度检索（默认）
    retriever.search_type = "similarity"
    results = retriever.invoke(query)
    print("【similarity】返回最相似的K个结果")
    for doc in results:
        print(f"  - {doc.page_content[:50]}...")
    
    # 2. MMR（最大边际相关）检索
    retriever_mmr = VectorStoreRetriever(
        vectorstore=vectorstore,
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 20}  # fetch_k: 候选集大小
    )
    results_mmr = retriever_mmr.invoke(query)
    print("\n【MMR】在相关性和多样性之间取得平衡")
    for doc in results_mmr:
        print(f"  - {doc.page_content[:50]}...")
    
    # 3. 相似度阈值检索
    retriever_threshold = VectorStoreRetriever(
        vectorstore=vectorstore,
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.5}
    )
    results_threshold = retriever_threshold.invoke(query)
    print(f"\n【similarity_score_threshold】返回相似度>0.5的结果")
    for doc in results_threshold:
        print(f"  - {doc.page_content[:50]}...")


def demonstrate_metadata_filter():
    """演示元数据过滤"""
    retriever, vectorstore = create_vectorstore_retriever()
    
    # 创建带过滤的检索器
    filtered_retriever = VectorStoreRetriever(
        vectorstore=vectorstore,
        search_type="similarity",
        search_kwargs={
            "k": 3,
            "filter": {"topic": "机器学习"}  # 只返回topic为机器学习的文档
        }
    )
    
    query = "学习"
    print(f"\n查询: {query}")
    print("过滤条件: topic = '机器学习'\n")
    
    results = filtered_retriever.invoke(query)
    for doc in results:
        print(f"  - {doc.page_content[:50]}...")
        print(f"    主题: {doc.metadata.get('topic')}")


def demonstrate_with_chroma_details():
    """
    详细演示Chroma向量数据库的使用
    
    Chroma特点：
    - 开源向量数据库，专注于AI应用
    - 简单易用，Python原生
    - 支持持久化存储
    - 内置高效的距离计算
    """
    
    embeddings = OpenAIEmbeddings()
    
    # 创建带持久化的Chroma数据库
    vectorstore = Chroma(
        collection_name="my_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_db"  # 持久化目录
    )
    
    # 添加文档
    docs = [
        Document(page_content="今天天气晴朗", metadata={"weather": "sunny"}),
        Document(page_content="明天下雨", metadata={"weather": "rainy"}),
        Document(page_content="后天多云", metadata={"weather": "cloudy"}),
    ]
    
    vectorstore.add_documents(docs)
    
    # 检索
    query = "今天什么天气"
    results = vectorstore.similarity_search(query, k=2)
    
    print(f"查询: {query}")
    for doc in results:
        print(f"  - {doc.page_content}, 元数据: {doc.metadata}")
    
    # 删除集合（清理）
    # vectorstore.delete_collection()


def demonstrate_with_faiss():
    """
    FAISS向量数据库使用演示
    
    FAISS特点：
    - Facebook开源的高效向量搜索库
    - 支持多种索引类型
    - 适合大规模数据
    - 仅支持内存存储（需要配合其他方案实现持久化）
    """
    
    from langchain.docstore import InMemoryDocstore
    import faiss
    import numpy as np
    
    # 创建Embedding维度（text-embedding-3-small是1536维）
    d = 1536
    
    # 创建FAISS索引
    index = faiss.IndexFlatL2(d)  # L2距离索引
    
    # 创建向量数据库
    vectorstore = FAISS(
        embedding_function=OpenAIEmbeddings(),
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    
    # 添加文档
    docs = [
        Document(page_content="深度学习使用神经网络", metadata={"type": "DL"}),
        Document(page_content="机器学习是AI的分支", metadata={"type": "ML"}),
    ]
    
    vectorstore.add_documents(docs)
    
    # 检索
    query = "什么是深度学习"
    results = vectorstore.similarity_search(query, k=2)
    
    print(f"查询: {query}")
    for doc in results:
        print(f"  - {doc.page_content}")


# 异步检索示例
async def async_retrieval_example():
    """异步检索示例"""
    retriever, _ = create_vectorstore_retriever()
    
    queries = ["Python", "机器学习", "RAG"]
    
    # 批量异步检索
    import asyncio
    
    async def retrieve(query):
        return await retriever.ainvoke(query)
    
    results = await asyncio.gather(*[retrieve(q) for q in queries])
    
    for query, docs in zip(queries, results):
        print(f"\n查询: {query}")
        for doc in docs:
            print(f"  - {doc.page_content[:50]}...")


# 运行示例
if __name__ == "__main__":
    test_basic_retrieval()
    # demonstrate_search_types()
    # demonstrate_metadata_filter()
    # demonstrate_with_faiss()
