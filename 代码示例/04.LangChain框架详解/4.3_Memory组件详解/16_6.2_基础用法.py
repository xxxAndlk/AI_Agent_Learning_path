from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 初始化嵌入和向量存储
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 创建向量存储（用于存储对话历史）
vectorstore = FAISS.from_texts(
    ["初始占位文本"],  # 需要至少一个文档
    embedding=embeddings
)

# 创建向量检索内存
memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),  # 检索Top-3
    memory_key="chat_history",
    return_messages=True
)

# 创建对话链
llm = ChatOpenAI(model="gpt-5.4-mini")
conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

# 多轮对话
dialogues = [
    "我最喜欢的编程语言是Python，它简单易学。",
    "我还想学习Web开发，有什么框架推荐？",
    "我计划做一个数据分析项目。",
    "我之前提到过我喜欢什么？",
    "我之前说想做什么项目？"
]

for user_input in dialogues:
    print(f"\n用户: {user_input}")
    response = conversation.predict(input=user_input)
    print(f"AI: {response}")
    
    # 显示检索到的历史
    print("\n检索到的相关历史:")
    docs = vectorstore.similarity_search(user_input, k=2)
    for doc in docs:
        print(f"  - {doc.page_content[:50]}...")
