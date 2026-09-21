from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnablePassthrough

llm = ChatOpenAI(model="gpt-5.4-mini")

# 定义Memory（旧版类仅作迁移对照；v1.x 推荐 ChatMessageHistory + RunnableWithMessageHistory）
memory = ConversationBufferWindowMemory(
    memory_key="history",
    return_messages=True,
    k=3
)

# 创建可运行对象
def get_history_messages(inputs):
    """获取历史消息"""
    return memory.load_memory_variables(inputs)["history"]

def save_to_memory(inputs, output):
    """保存到内存"""
    memory.save_context(inputs, output)

# LCEL链
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个AI助手。"),
    MessagesPlaceholder(variable_name="history", optional=True),
    ("human", "{input}")
])

chain = (
    RunnablePassthrough.assign(
        history=lambda x: get_history_messages(x)  # 返回历史消息列表
    )
    | prompt
    | llm
)

# 手动处理记忆（LCEL方式）
def invoke_with_memory(user_input: str):
    """带内存调用的辅助函数"""
    # 获取当前输入
    inputs = {"input": user_input}
    
    # 调用链
    response = chain.invoke(inputs)
    
    # 保存上下文
    memory.save_context(inputs, response)
    
    return response

# 测试
for i in range(3):
    result = invoke_with_memory(f"测试问题{i+1}")
    print(f"Q{i+1}: {result.content}")
