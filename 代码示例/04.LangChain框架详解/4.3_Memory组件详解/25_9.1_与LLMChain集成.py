from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

llm = ChatOpenAI(model="gpt-5.4-mini")

# 按会话创建内存（生产环境可换成 Redis/数据库后端）
session_histories = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]

# 创建Prompt模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的AI助手，擅长回答各类问题。"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

# 创建LCEL链并用 RunnableWithMessageHistory 包装
chain = prompt | llm

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

# 多轮对话
questions = [
    "什么是机器学习？",
    "它和深度学习有什么区别？",
    "TensorFlow是做什么的？"
]

for q in questions:
    response = chain_with_history.invoke(
        {"question": q},
        config={"configurable": {"session_id": "user_001"}}
    )
    print(f"\n问: {q}")
    print(f"答: {response.content}")
