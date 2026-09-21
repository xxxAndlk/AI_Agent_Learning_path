from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

llm = ChatOpenAI(model="gpt-5.4-mini")

memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True,
    
    # Token控制
    max_token_limit=1000,  # 超过此值开始摘要旧消息
    
    # 自定义消息处理
    output_key="text",
    input_key="input",
    
    # 消息前缀（用于摘要）
    human_prefix="用户",
    ai_prefix="AI",
    
    # 预加载现有消息
    chat_memory=...  # 可以传入已有的ChatMessageHistory
)

# 手动添加消息
memory.chat_memory.add_message(HumanMessage(content="你好"))
memory.chat_memory.add_message(AIMessage(content="你好！"))
