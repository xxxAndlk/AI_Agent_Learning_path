"""
RunnableParallel并行执行示例
展示如何高效地并行处理多个任务
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import time

llm = ChatOpenAI()

# ============================================================
# 基本并行执行
# ============================================================

# 定义三个独立的处理分支
# 分支1：解释概念
explain_prompt = ChatPromptTemplate.from_template("解释{topic}的基本概念")
explain_chain = explain_prompt | llm | StrOutputParser()

# 分支2：分析优缺点
proscons_prompt = ChatPromptTemplate.from_template("分析{topic}的优缺点")
proscons_chain = proscons_prompt | llm | StrOutputParser()

# 分支3：给出应用场景
applications_prompt = ChatPromptTemplate.from_template("列出{topic}的3个应用场景")
applications_chain = applications_prompt | llm | StrOutputParser()

# 使用RunnableParallel组合三个分支
# 输入会同时发送给三个分支，每个分支独立处理
parallel_chain = RunnableParallel(
    explain=explain_chain,
    proscons=proscons_chain,
    applications=applications_chain
)

# 测量执行时间
start_time = time.time()
result = parallel_chain.invoke({"topic": "区块链"})
end_time = time.time()

print(f"并行执行耗时: {end_time - start_time:.2f}秒")
print(f"解释: {result['explain'][:100]}...")
print(f"优缺点: {result['proscons'][:100]}...")
print(f"应用场景: {result['applications'][:100]}...")

# ============================================================
# 对比：串行执行的时间
# ============================================================
start_time = time.time()
explain_result = explain_chain.invoke({"topic": "区块链"})
proscons_result = proscons_chain.invoke({"topic": "区块链"})
applications_result = applications_chain.invoke({"topic": "区块链"})
end_time = time.time()

print(f"\n串行执行耗时: {end_time - start_time:.2f}秒")
print(f"并行相比串行节省时间: {end_time - start_time - (end_time - start_time):.2f}秒")
