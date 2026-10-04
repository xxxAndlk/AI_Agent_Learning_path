"""
RunnableSequence动态修改示例
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

llm = ChatOpenAI()
base_prompt = ChatPromptTemplate.from_template("用中文回答：{question}")

# 基础链
base_chain = base_prompt | llm | StrOutputParser()

# ============================================================
# 使用assign动态添加步骤
# ============================================================

# 添加一个后处理步骤，将答案转换为大写
def to_uppercase(result):
    return result.upper()

upper_chain = base_chain.assign(
    post_process=RunnableLambda(to_uppercase)
)

# 执行时会自动调用后处理步骤
result = upper_chain.invoke({"question": "什么是AI"})
print(f"大写结果: {result}")
