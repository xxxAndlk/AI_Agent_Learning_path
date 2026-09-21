"""
LCEL错误处理最佳实践
展示如何优雅地处理各种错误情况
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.retry import RetryRunnable
from langchain_core.callbacks import BaseCallbackHandler
import time

# ============================================================
# 方式1：使用with_retry添加重试机制
# ============================================================

llm = ChatOpenAI()
chain = (
    ChatPromptTemplate.from_template("{question}")
    | llm
    | StrOutputParser()
)

# 添加重试机制
# max_attempt_number: 最大重试次数
# wait_exponential_min: 最小等待时间（秒）
# wait_exponential_max: 最大等待时间（秒）
retry_chain = chain.with_retry(
    max_attempt_number=3,
    wait_exponential_min=1,
    wait_exponential_max=10
)

# ============================================================
# 方式2：使用RunnableLambda添加自定义错误处理
# ============================================================

def safe_invoke(chain, inputs, max_retries=3):
    """带重试的调用包装器"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            last_error = e
            print(f"尝试 {attempt + 1} 失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
    
    raise last_error

# 使用自定义包装器
try:
    result = safe_invoke(chain, {"question": "什么是LCEL？"})
    print(f"成功: {result}")
except Exception as e:
    print(f"最终失败: {e}")

# ============================================================
# 方式3：使用fallback提供备选方案
# ============================================================

from langchain_core.runnables import RunnableBranch

# 主链：使用GPT-5.4
main_chain = (
    ChatPromptTemplate.from_template("{question}")
    | ChatOpenAI(model="gpt-5.4")
    | StrOutputParser()
)

# 备用链：使用GPT-5.4-nano（更快但可能不够准确）
fallback_chain = (
    ChatPromptTemplate.from_template("{question}")
    | ChatOpenAI(model="gpt-5.4-mini")
    | StrOutputParser()
)

# 注意：LangChain的fallback机制可以通过配置实现
# 这里展示概念

# ============================================================
# 方式4：添加回调监控错误
# ============================================================

class ErrorTrackingCallback(BaseCallbackHandler):
    """错误追踪回调"""
    
    def __init__(self):
        self.errors = []
    
    def on_chain_error(self, error: Exception, **kwargs):
        """当链执行出错时调用"""
        self.errors.append({
            "error": str(error),
            "timestamp": time.time(),
            "inputs": kwargs.get("inputs", {})
        })
        print(f"捕获错误: {error}")

# 创建带错误追踪的链
error_callback = ErrorTrackingCallback()
chain_with_tracking = (
    ChatPromptTemplate.from_template("{question}")
    | llm
    | StrOutputParser()
)

# ============================================================
# 方式5：超时控制
# ============================================================

from langchain_core.runnables import timeout

# 添加超时控制（假设支持）
# 超时后抛出TimeoutException
# timeout_chain = timeout(30)(chain)  # 30秒超时
