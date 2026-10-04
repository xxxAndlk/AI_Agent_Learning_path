from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
import time

llm = ChatOpenAI(model="gpt-5.4-mini")

# 记录摘要生成时间
memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="history",
    return_messages=True
)

# 批量测试性能
start_time = time.time()
for i in range(10):
    memory.save_context(
        {"input": f"用户问题{i}"},
        {"text": f"AI回答{i}"}
    )
elapsed = time.time() - start_time

print(f"10轮对话保存耗时: {elapsed:.2f}秒")
print(f"平均每轮: {elapsed/10:.3f}秒")
print(f"当前摘要: {memory.moving_summary[:100]}...")
