from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import uuid

def faiss_with_ids():
    """使用自定义ID的FAISS索引"""
    
    # 文档和对应ID
    docs = [
        "Python是一种高级编程语言",
        "JavaScript主要用于Web开发",
        "Go语言以并发著称",
    ]
    
    # 生成唯一ID
    ids = [str(uuid.uuid4()) for _ in docs]
    
    embeddings = OpenAIEmbeddings()
    
    # 从文本创建，带自定义ID
    vectorstore = FAISS.from_texts(
        texts=docs,
        embedding=embeddings,
        ids=ids
    )
    
    # 搜索
    query = "什么语言擅长并发？"
    results = vectorstore.similarity_search_with_score(query, k=2)
    
    print(f"查询: {query}\n")
    for doc, score in results:
        print(f"内容: {doc.page_content}")
        print(f"ID: {doc.metadata.get('id', 'N/A')}")
        print(f"相似度分数: {score:.4f}\n")

# faiss_with_ids()  # 需要API密钥
