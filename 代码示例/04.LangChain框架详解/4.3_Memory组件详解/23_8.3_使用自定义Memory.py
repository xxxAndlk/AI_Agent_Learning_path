from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 使用自定义内存
custom_memory = CustomDatabaseMemory(
    storage_path="my_conversation.json",
    max_turns=5
)

llm = ChatOpenAI(model="gpt-5.4-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手。"),
    MessagesPlaceholder(variable_name="conversation_history"),
    ("human", "{input}")
])

conversation = ConversationChain(
    llm=llm,
    memory=custom_memory,
    prompt=prompt
)

# 测试自定义内存
for i in range(3):
    response = conversation.predict(input=f"测试对话{i+1}")
    print(f"用户: 测试对话{i+1}")
    print(f"AI: {response}\n")

# 查看保存的文件
print("保存的历史文件内容:")
with open("my_conversation.json", "r", encoding="utf-8") as f:
    print(f.read())
