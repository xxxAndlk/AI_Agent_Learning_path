from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

def create_faiss_retriever():
    """创建FAISS retriever"""
    
    # 创建测试文档
    docs = [
        Document(
            page_content="机器学习是人工智能的一个分支",
            metadata={"source": "ai.txt", "page": 1}
        ),
        Document(
            page_content="深度学习使用神经网络模型",
            metadata={"source": "dl.txt", "page": 1}
        ),
        Document(
            page_content="Transformer模型改变了NLP领域",
            metadata={"source": "nlp.txt", "page": 1}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    
    # 创建向量存储
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # 转换为retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",  # 或 "mmr", "similarity_threshold"
        search_kwargs={
            "k": 2,                  # 返回数量
            # "score_threshold": 0.8  # 相似度阈值
        }
    )
    
    # 使用retriever
    query = "神经网络相关的内容"
    results = retriever.invoke(query)
    
    print(f"查询: {query}\n")
    for doc in results:
        print(f"内容: {doc.page_content}")
        print(f"来源: {doc.metadata}\n")

# create_faiss_retriever()  # 需要API密钥
