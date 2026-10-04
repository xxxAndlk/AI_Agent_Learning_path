"""
LCEL异步基础示例
展示异步调用模式
"""

import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建链
llm = ChatOpenAI()
chain = (
    ChatPromptTemplate.from_template("用一句话介绍{topic}")
    | llm
    | StrOutputParser()
)

# ============================================================
# 示例1：基础异步调用
# ============================================================

async def basic_async():
    """最基本的异步调用方式"""
    result = await chain.ainvoke({"topic": "人工智能"})
    print(f"异步结果: {result}")
    return result

# 运行异步函数
result = asyncio.run(basic_async())

# ============================================================
# 示例2：并发多个异步请求
# ============================================================

async def concurrent_async():
    """并发执行多个异步请求"""
    topics = ["机器学习", "深度学习", "自然语言处理", "计算机视觉"]
    
    # 方式1：使用asyncio.gather并发执行
    tasks = [chain.ainvoke({"topic": topic}) for topic in topics]
    results = await asyncio.gather(*tasks)
    
    for topic, result in zip(topics, results):
        print(f"{topic}: {result[:30]}...")
    
    return results

asyncio.run(concurrent_async())

# ============================================================
# 示例3：异步流式输出
# ============================================================

async def async_stream():
    """异步流式输出"""
    print("异步流式输出: ", end="")
    
    # astream返回异步生成器
    async for chunk in chain.astream({"topic": "量子计算"}):
        print(chunk, end="", flush=True)
    print()

asyncio.run(async_stream())

# ============================================================
# 示例4：批量异步处理
# ============================================================

async def batch_async():
    """批量异步处理"""
    inputs = [
        {"topic": "区块链"},
        {"topic": "云计算"},
        {"topic": "物联网"},
        {"topic": "大数据"}
    ]
    
    # abatch自动进行批量优化
    results = await chain.abatch(inputs)
    
    for result in results:
        print(f"批量结果: {result[:40]}...")
    
    return results

asyncio.run(batch_async())
