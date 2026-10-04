from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory
)
from langchain_openai import ChatOpenAI
import time

llm = ChatOpenAI(model="gpt-5.4-mini")

# 对比不同内存类型的性能
memory_types = {
    "Buffer": ConversationBufferMemory(memory_key="history", return_messages=True),
    "Window(k=5)": ConversationBufferWindowMemory(k=5, memory_key="history", return_messages=True),
    "Summary": ConversationSummaryMemory(llm=llm, memory_key="history", return_messages=True),
    "SummaryBuffer": ConversationSummaryBufferMemory(llm=llm, memory_key="history", max_token_limit=500)
}

# 模拟50轮对话
num_turns = 50

for name, memory in memory_types.items():
    start = time.time()
    
    for i in range(num_turns):
        memory.save_context(
            {"input": f"用户问题{i}"},
            {"text": f"AI回答{i}"}
        )
    
    elapsed = time.time() - start
    
    # 估算存储效率
    if hasattr(memory, 'moving_summary_buffer'):
        summary_len = len(memory.moving_summary_buffer)
    else:
        summary_len = 0
    
    if hasattr(memory, 'chat_memory'):
        buffer_count = len(memory.chat_memory.messages)
    else:
        buffer_count = 0
    
    print(f"{name}:")
    print(f"  耗时: {elapsed:.2f}秒")
    print(f"  消息数: {buffer_count}, 摘要长度: {summary_len}")
    print()
