from langchain.memory import ConversationEntityMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory.entity import EntityStore, InMemoryEntityStore

llm = ChatOpenAI(model="gpt-5.4-mini")

# 创建实体内存
memory = ConversationEntityMemory(
    llm=llm,
    memory_key="history",
    return_messages=True,
    entity_store=InMemoryEntityStore()  # 内存存储，也可换向量存储
)

# 创建对话链
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 包含实体信息的对话
dialogues = [
    "我叫张三，是一名软件工程师。",
    "我和同事Alice一起做项目。",
    "我们正在开发一个AI产品，名字叫SmartAssistant。",
    "项目将在下周发布。",
    "我是谁？",
    "我和谁一起做项目？",
    "产品叫什么名字？"
]

for user_input in dialogues:
    print(f"\n用户: {user_input}")
    response = conversation.predict(input=user_input)
    print(f"AI: {response}")
    
    # 查看提取的实体
    print("\n当前实体:")
    entities = memory.entity_store.get_all()
    for entity_name, entity_data in entities.items():
        print(f"  {entity_name}: {entity_data}")
