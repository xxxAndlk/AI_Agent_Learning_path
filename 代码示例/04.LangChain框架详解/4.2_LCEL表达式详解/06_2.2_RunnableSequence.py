"""
RunnableSequence详解
深入理解管道操作符返回的类型
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence

llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_template("解释{concept}的核心原理")
output_parser = StrOutputParser()

# 创建RunnableSequence
chain = prompt | llm | output_parser

# ============================================================
# RunnableSequence的属性和方法
# ============================================================

# first属性：获取链中的第一个组件
# 返回Runnable对象，这里是ChatPromptTemplate
first_component = chain.first
print(f"第一个组件: {first_component}")

# last属性：获取链中的最后一个组件
# 返回Runnable对象，这里是StrOutputParser
last_component = chain.last
print(f"最后一个组件: {last_component}")

# middle属性：获取中间的所有组件（不含首尾）
# 返回Runnable序列
middle_components = chain.middle
print(f"中间组件: {middle_components}")

# steps属性：获取完整步骤列表
# 返回元组列表，每个元组包含(步骤名, Runnable对象)
all_steps = chain.steps
print(f"所有步骤: {all_steps}")

# verbose属性：控制是否打印详细信息
# 启用后，每次执行都会打印输入输出，便于调试
chain.verbose = True

# 调用invoke时会打印详细的执行过程
result = chain.invoke({"concept": "机器学习"})
