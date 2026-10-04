from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

# 使用专门的LLM生成摘要（可以用更便宜的模型）
llm = ChatOpenAI(model="gpt-5.4-mini")
summary_llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

# 创建摘要内存
memory = ConversationSummaryMemory(
    llm=summary_llm,  # 用于生成摘要的LLM
    memory_key="history",
    return_messages=True
)

# 创建对话链
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 模拟多轮对话
dialogues = [
    "我想学习Python，请给我一些建议。",
    "谢谢！那数据分析该怎么学？",
    "机器学习感兴趣吗？",
    "深度学习呢？",
    "我想深入学习TensorFlow"
]

for user_input in dialogues:
    response = conversation.predict(input=user_input)
    print(f"用户: {user_input}")
    print(f"AI: {response}\n")
    print(f"[摘要长度: {len(memory.moving_summary)}字符]")
    print("-" * 50)
