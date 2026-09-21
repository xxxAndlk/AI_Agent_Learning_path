from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import time

# 性能测试
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(["初始"], embedding=embeddings)

memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    memory_key="history"
)

llm = ChatOpenAI(model="gpt-5.4-mini")

# 测试不同规模下的检索性能
for n_messages in [10, 50, 100, 500]:
    # 预先添加消息
    for i in range(n_messages):
        memory.save_context(
            {"input": f"问题{i}"},
            {"text": f"回答{i}"}
        )
    
    # 测试检索速度
    start = time.time()
    for _ in range(10):
        memory.load_memory_variables({"input": "测试查询"})
    elapsed = time.time() - start
    
    print(f"{n_messages}条消息: 平均检索时间 {elapsed/10*1000:.1f}ms")
