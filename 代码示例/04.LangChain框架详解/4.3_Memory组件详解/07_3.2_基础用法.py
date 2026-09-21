from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOpenAI(model="gpt-5.4-mini")

# 创建窗口内存，保留最近3轮对话
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    return_messages=True,
    k=3  # 保留最近3轮（6条消息，用户+AI各一条算1轮）
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的AI助手。"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

# 对话10轮，观察窗口效果
for i in range(10):
    chain.invoke({"input": f"这是第{i+1}轮对话"})
    msg_count = len(memory.chat_memory.messages)
    print(f"第{i+1}轮后，内存中有{msg_count}条消息")
