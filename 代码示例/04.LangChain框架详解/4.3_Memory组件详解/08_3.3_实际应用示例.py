from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-5.4-mini")

# 创建窗口记忆，k=2表示保留最近2轮对话
memory = ConversationBufferWindowMemory(
    k=2,
    return_messages=True,
    memory_key="history"
)

# 使用ConversationChain（简化版的对话链）
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True  # 显示详细信息
)

# 模拟多轮对话
dialogues = [
    "我想学习Python，请推荐一些入门资源。",
    "谢谢！那数据分析方面有什么推荐吗？",
    "好的，我还想了解Web开发。",
    "机器学习呢？有什么建议？",
    "回到第一个问题，你推荐了什么资源？"
]

for user_input in dialogues:
    print(f"\n用户: {user_input}")
    response = conversation.predict(input=user_input)
    print(f"AI: {response}")
    print(f"--- 内存消息数: {len(memory.chat_memory.messages)} ---")
