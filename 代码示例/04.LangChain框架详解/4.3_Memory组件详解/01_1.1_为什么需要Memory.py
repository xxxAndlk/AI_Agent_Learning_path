# ❌ 无Memory：每次调用都是独立的
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
response1 = llm.invoke("我叫张三")
response2 = llm.invoke("我叫什么名字？")  # 模型不知道你是谁

# ✅ 有Memory：自动维护对话历史（v1.x：LCEL + ChatMessageHistory 组合）
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

memory = ChatMessageHistory()

prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm

chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: memory,  # 演示用单会话；生产环境按 session_id 返回独立历史
    input_messages_key="input",
    history_messages_key="history",
)

chain_with_history.invoke(
    {"input": "我叫张三"},
    config={"configurable": {"session_id": "demo"}},
)
response = chain_with_history.invoke(
    {"input": "我叫什么名字？"},  # 可以正确回答
    config={"configurable": {"session_id": "demo"}},
)
