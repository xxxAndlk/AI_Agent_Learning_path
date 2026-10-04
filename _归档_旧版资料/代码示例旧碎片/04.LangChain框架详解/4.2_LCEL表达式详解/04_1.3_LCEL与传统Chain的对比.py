"""
LCEL方式：简洁的管道组合
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

llm = ChatOpenAI()

# 使用LCEL，一行代码完成所有组合
chain = (
    {"content": RunnablePassthrough()}
    | ChatPromptTemplate.from_template("把以下内容转换成3个问题：{content}")
    | llm
    | StrOutputParser()
)

# LCEL方式只需要约15行代码，而且更加清晰和可维护
