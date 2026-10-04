from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma, Pinecone, Milvus

# Chroma示例
vectorstore_chroma = Chroma.from_texts(
    texts=["初始文本"],
    embedding=OpenAIEmbeddings(),
    collection_name="conversation_history"
)

memory_chroma = VectorStoreRetrieverMemory(
    retriever=vectorstore_chroma.as_retriever(search_kwargs={"k": 5}),
    memory_key="history"
)

# Pinecone示例（云端向量数据库）
# 需要先配置Pinecone API
# from pinecone import Pinecone
# pc = Pinecone(api_key="your-api-key")
# index = pc.Index("conversation-memory")
# vectorstore_pinecone = PineconeVectorStore(
#     index=index,
#     embedding=OpenAIEmbeddings(),
#     text_key="text"
# )

# Milvus示例（本地/云端向量数据库）
# vectorstore_milvus = Milvus.from_texts(
#     texts=["初始文本"],
#     embedding=OpenAIEmbeddings(),
#     connection_args={"host": "localhost", "port": "19530"}
# )
