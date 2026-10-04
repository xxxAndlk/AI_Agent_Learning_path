from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os

def persist_faiss():
    """FAISS持久化"""
    
    # 文档
    docs = [
        "RAG技术结合了检索和生成",
        "向量数据库存储嵌入向量",
        "LangChain简化了LLM应用开发",
    ]
    
    embeddings = OpenAIEmbeddings()
    
    # 创建向量存储
    vectorstore = FAISS.from_texts(docs, embeddings)
    
    # 保存到本地
    persist_directory = "./faiss_index"
    vectorstore.save_local(persist_directory)
    
    print(f"索引已保存到: {persist_directory}")
    
    # 加载
    loaded_vectorstore = FAISS.load_local(
        persist_directory,
        embeddings,
        allow_dangerous_deserialization=True  # 信任来源时启用
    )
    
    # 使用加载的索引
    results = loaded_vectorstore.similarity_search("RAG是什么？", k=2)
    print("\n加载后搜索结果:")
    for doc in results:
        print(f"  - {doc.page_content}")

# persist_faiss()  # 需要API密钥
