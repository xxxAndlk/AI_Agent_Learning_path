"""
构建基础链的完整示例
涵盖从简单到复杂的各种场景
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any

llm = ChatOpenAI(model="gpt-5.4-mini")

# ============================================================
# 示例1：最简单的问答链
# ============================================================

# 一步创建：Prompt模板 + LLM + 输出解析器
simple_qa = (
    ChatPromptTemplate.from_template("{question}")
    | llm
    | StrOutputParser()
)

result = simple_qa.invoke({"question": "什么是LCEL？"})
print(f"简单问答: {result[:100]}...")

# ============================================================
# 示例2：带系统提示的问答链
# ============================================================

# 使用from_messages创建多轮对话模板
system_qa = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}，用专业的语言回答问题。"),
    ("human", "{question}")
])

qa_chain = system_qa | llm | StrOutputParser()

result = qa_chain.invoke({
    "role": "技术顾问",
    "question": "如何优化数据库查询性能？"
})
print(f"系统提示链: {result[:100]}...")

# ============================================================
# 示例3：带上下文的问答链
# ============================================================

# 用于RAG场景，需要先检索上下文
context_qa = (
    ChatPromptTemplate.from_template(
        "基于以下上下文回答问题。\n\n上下文：{context}\n\n问题：{question}\n\n答案："
    )
    | llm
    | StrOutputParser()
)

result = context_qa.invoke({
    "context": "LCEL是LangChain的表达式语言，用于构建处理管道。",
    "question": "什么是LCEL？"
})
print(f"上下文问答: {result}")

# ============================================================
# 示例4：多轮对话链
# ============================================================

# 需要保留对话历史的多轮对话
conversation_qa = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手。"),
    MessagesPlaceholder(variable_name="history"),  # 对话历史
    ("human", "{input}")  # 当前输入
])

# 注意：完整的对话链需要配合Memory使用
# 这里展示基础结构
conv_chain = conversation_qa | llm | StrOutputParser()

# 模拟第一轮对话
first_response = conv_chain.invoke({
    "history": [],
    "input": "我喜欢机器学习"
})
print(f"第一轮: {first_response}")

# 模拟第二轮（需要手动维护history）
second_response = conv_chain.invoke({
    "history": [
        ("human", "我喜欢机器学习"),
        ("ai", first_response)
    ],
    "input": "有什么推荐的学习资源吗？"
})
print(f"第二轮: {second_response}")
