"""
LangChain Memory系统实现
演示如何维护对话上下文和长期记忆
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# ============================================================
# 步骤1：创建消息历史存储
# ============================================================
# ChatMessageHistory内存存储对话历史
# 实际项目可使用Redis、数据库等持久化存储
session_histories = {}

def get_session_history(session_id: str):
    """
    获取或创建会话历史
    用于管理多用户/多会话的独立对话上下文
    """
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]

# ============================================================
# 步骤2：定义带历史的Prompt
# ============================================================
# MessagesPlaceholder(variable_name="history")会被自动填充历史消息
# 保持对话的连续性，让模型理解上下文
prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的对话助手，记住之前的对话内容。"),
    MessagesPlaceholder(variable_name="history"),  # 自动插入历史消息
    ("human", "{input}")
])

# ============================================================
# 步骤3：创建基础链
# ============================================================
llm = ChatOpenAI(model="gpt-5.4-mini")
chain = prompt_with_history | llm

# ============================================================
# 步骤4：包装为带历史的链
# ============================================================
# RunnableWithMessageHistory自动管理：
# - 从存储加载历史
# - 添加到Prompt
# - 保存新消息到存储
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# ============================================================
# 步骤5：多轮对话示例
# ============================================================
session_id = "user_123"

# 第一轮
response1 = chain_with_history.invoke(
    {"input": "我叫张三，是一名软件工程师。"},
    config={"configurable": {"session_id": session_id}}
)
print(f"AI: {response1.content}")

# 第二轮（AI应该记得用户名字）
response2 = chain_with_history.invoke(
    {"input": "你还记得我的名字吗？"},
    config={"configurable": {"session_id": session_id}}
)
print(f"AI: {response2.content}")

# 查看完整对话历史
history = get_session_history(session_id)
print("\n完整对话历史：")
for msg in history.messages:
    print(f"{msg.type}: {msg.content}")
