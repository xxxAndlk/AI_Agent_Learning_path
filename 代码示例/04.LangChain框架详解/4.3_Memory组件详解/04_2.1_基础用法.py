from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 初始化LLM
llm = ChatOpenAI(model="gpt-5.4-mini")

# 创建Memory
memory = ConversationBufferMemory(
    memory_key="chat_history",  # 变量名，在prompt中引用
    return_messages=True,       # 返回消息对象列表，而非字符串
    output_key="text",          # 从输出中提取什么作为AI回复
    input_key="input"           # 从输入中提取什么作为用户输入
)

# 创建Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的AI助手。"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# 创建Chain
chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

# 多轮对话
response1 = chain.invoke({"input": "我喜欢编程，特别喜欢Python"})
print(f"用户: 我喜欢编程，特别喜欢Python")
print(f"AI: {response1['text']}\n")

response2 = chain.invoke({"input": "我刚才说我喜欢什么？"})
print(f"用户: 我刚才说我喜欢什么？")
print(f"AI: {response2['text']}\n")

# 查看内存中的内容
print("内存内容:")
for msg in memory.chat_memory.messages:
    print(f"  {type(msg).__name__}: {msg.content}")
