"""
LCEL性能优化最佳实践
涵盖常见场景的优化方案
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
import time

# ============================================================
# 优化1：减少不必要的组件
# ============================================================

# 性能对比：完整链 vs 简化链
llm = ChatOpenAI()

# 完整链：每个步骤都有开销
full_chain = (
    ChatPromptTemplate.from_template("{question}")
    | llm
    | StrOutputParser()
)

# 在高频调用场景下，可以考虑：
# 1. 预编译Prompt模板（ChatPromptTemplate已经是预编译的）
# 2. 复用LLM实例
# 3. 减少不必要的中间步骤

# ============================================================
# 优化2：合理使用批处理
# ============================================================

prompt = ChatPromptTemplate.from_template("用一句话介绍{topic}")
chain = prompt | llm | StrOutputParser()

# 错误方式：循环调用
topics = ["AI", "ML", "DL", "NLP", "CV"]
start = time.time()
for topic in topics:
    chain.invoke({"topic": topic})
loop_time = time.time() - start

# 正确方式：批量调用
start = time.time()
inputs = [{"topic": topic} for topic in topics]
results = chain.batch(inputs)
batch_time = time.time() - start

print(f"循环调用耗时: {loop_time:.2f}秒")
print(f"批量调用耗时: {batch_time:.2f}秒")
print(f"批量优化提升: {loop_time/batch_time:.2f}倍")

# ============================================================
# 优化3：使用流式减少等待时间
# ============================================================

# 对于需要立即响应的场景，使用流式可以显著改善用户体验
# 因为用户可以在完整响应生成之前就开始看到内容

# 非流式：等待完整响应
start = time.time()
result = chain.invoke({"topic": "量子计算"})
ttfb_non_stream = time.time() - start  # Time To First Byte

# 流式：立即开始返回
start = time.time()
first_token_time = None
for i, chunk in enumerate(chain.stream({"topic": "量子计算"})):
    if i == 0:
        first_token_time = time.time() - start

print(f"非流式首字节时间: {ttfb_non_stream:.2f}秒")
print(f"流式首字节时间: {first_token_time:.3f}秒")

# ============================================================
# 优化4：配置合适的LLM参数
# ============================================================

# 根据场景选择合适的参数
llm_fast = ChatOpenAI(
    model="gpt-5.4-mini",  # 更快的模型
    temperature=0,          # 确定性输出
    max_tokens=100          # 限制输出长度
)

llm_accurate = ChatOpenAI(
    model="gpt-5.4",          # 更准确的模型
    temperature=0.3,        # 适度创造性
    max_tokens=1000         # 完整输出
)

# ============================================================
# 优化5：连接池和复用
# ============================================================

# 在应用级别复用LLM实例，避免重复创建的开销
# 推荐方式：在应用启动时创建一次，全局复用

# 全局LLM实例（单例模式）
class LLMManager:
    _instance = None
    _llm = None
    
    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            cls._llm = ChatOpenAI()
        return cls._llm

# 使用
llm = LLMManager.get_llm()
