# 安装依赖
# pip install langchain langchain-community langchain-openai faiss-cpu

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

# 1. 准备文档
documents = [
    "FAISS是Facebook开源的向量相似度搜索库",
    "FAISS支持多种索引类型，包括Flat、IVF、HNSW、PQ",
    "HNSW索引提供超快的搜索速度",
    "乘积量化可以大幅压缩向量存储空间",
    "LangChain可以方便地集成FAISS作为向量数据库",
]

# 2. 创建文本分割器
splitter = CharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0
)

# 3. 创建embeddings
# 注意：需要设置OPENAI_API_KEY环境变量
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 4. 创建FAISS向量存储
# 从文本创建
vectorstore = FAISS.from_texts(
    documents,
    embedding=embeddings
)

# 5. 执行相似度搜索
query = "FAISS支持哪些索引类型？"
results = vectorstore.similarity_search(query, k=2)

print("查询:", query)
print("\n检索结果:")
for i, doc in enumerate(results):
    print(f"\n结果 {i+1}:")
    print(f"  内容: {doc.page_content}")
    print(f"  元数据: {doc.metadata}")
