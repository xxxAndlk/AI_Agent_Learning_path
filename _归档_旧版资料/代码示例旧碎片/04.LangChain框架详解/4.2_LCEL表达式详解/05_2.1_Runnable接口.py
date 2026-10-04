"""
Runnable接口详解
本示例展示Runnable接口的所有核心方法
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

# 创建基础组件
llm = ChatOpenAI(model="gpt-5.4-mini")
prompt = ChatPromptTemplate.from_template("用一句话介绍{topic}")
chain = prompt | llm | StrOutputParser()

# ============================================================
# Runnable接口的核心方法
# ============================================================

# 1. invoke - 同步调用，最常用的方法
# 接收任意类型的输入，返回对应类型的输出
# 对于Chain，输入通常是一个字典，输出通常是处理后的结果
result = chain.invoke({"topic": "量子计算"})
print(f"invoke结果: {result}")

# 2. ainvoke - 异步调用，适合高并发场景
# 返回一个协程，需要使用await等待结果
import asyncio

async def async_invoke():
    result = await chain.ainvoke({"topic": "量子计算"})
    print(f"ainvoke结果: {result}")

asyncio.run(async_invoke())

# 3. stream - 同步流式输出
# 返回一个生成器，每次迭代返回一个chunk
# 适合需要实时显示输出的场景（如聊天机器人）
print("stream输出: ", end="")
for chunk in chain.stream({"topic": "量子计算"}):
    print(chunk, end="", flush=True)
print()

# 4. astream - 异步流式输出
# 结合了异步和流式的优势，适合高并发实时应用
async def async_stream():
    print("astream输出: ", end="")
    async for chunk in chain.astream({"topic": "量子计算"}):
        print(chunk, end="", flush=True)
    print()

asyncio.run(async_stream())

# 5. batch - 批量同步处理
# 接收输入列表，一次性处理多个请求
# 内部会进行优化，可能使用批量API或并行处理
inputs = [
    {"topic": "量子计算"},
    {"topic": "区块链"},
    {"topic": "人工智能"}
]
results = chain.batch(inputs)
for i, result in enumerate(results):
    print(f"batch结果{i+1}: {result}")

# 6. abatch - 批量异步处理
async def async_batch():
    results = await chain.abatch(inputs)
    return results

results = asyncio.run(async_batch())
