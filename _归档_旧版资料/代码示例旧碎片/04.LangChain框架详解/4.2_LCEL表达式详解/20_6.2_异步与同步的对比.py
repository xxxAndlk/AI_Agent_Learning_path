"""
异步与同步性能对比
帮助选择合适的调用方式
"""

import asyncio
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI()
chain = (
    ChatPromptTemplate.from_template("用一句话介绍{topic}")
    | llm
    | StrOutputParser()
)

topics = ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "机器人"]

# ============================================================
# 同步执行时间
# ============================================================

start = time.time()
for topic in topics:
    chain.invoke({"topic": topic})
sync_time = time.time() - start
print(f"同步执行耗时: {sync_time:.2f}秒")

# ============================================================
# 异步执行时间
# ============================================================

async def run_async():
    start = time.time()
    tasks = [chain.ainvoke({"topic": topic}) for topic in topics]
    await asyncio.gather(*tasks)
    async_time = time.time() - start
    print(f"异步执行耗时: {async_time:.2f}秒")
    print(f"性能提升: {sync_time/async_time:.2f}倍")
    return async_time

asyncio.run(run_async())

# ============================================================
# 何时使用异步
# ============================================================

"""
性能对比分析：

1. 同步执行：
   - 优点：代码简单，易于理解和调试
   - 缺点：并发能力有限，阻塞等待
   - 适用：低并发、简单场景、脚本工具

2. 异步执行：
   - 优点：高并发、低延迟、资源利用率高
   - 缺点：代码复杂度稍高，需要理解async/await
   - 适用：高并发API服务、Web应用、实时系统

在实际的Web服务中，如果每个请求需要调用LLM，
使用异步可以将吞吐量提高3-5倍。
"""
