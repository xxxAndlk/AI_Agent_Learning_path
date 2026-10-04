from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

llm = ChatOpenAI(model="gpt-5.4-mini")

# 创建混合内存
memory = ConversationSummaryBufferMemory(
    llm=llm,                    # 用于生成摘要的LLM
    memory_key="history",
    return_messages=True,
    max_token_limit=500,        # 超过500 tokens时将旧消息转为摘要
    moving_summary_buffer=""    # 初始摘要（可选）
)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 模拟多轮对话，观察token限制效果
for i in range(20):
    user_input = f"这是第{i+1}轮对话，我想学习关于话题{i}的内容。"
    response = conversation.predict(input=user_input)
    
    # 检查内存状态
    tokens = memory.predict_new_summary(
        memory.chat_memory.messages,
        memory.moving_summary_buffer
    )
    print(f"轮{i+1}: Buffer消息数={len(memory.chat_memory.messages)}, "
          f"摘要长度={len(memory.moving_summary_buffer)}")
