"""
LangChain流式输出和LangSmith追踪
生产环境常用的高级功能
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.tracers import LangChainTracer

# ============================================================
# 步骤1：配置回调处理器
# ============================================================
# StreamingStdOutCallbackHandler: 实时打印输出到控制台
# LangChainTracer: 发送追踪数据到LangSmith平台
callbacks = [
    StreamingStdOutCallbackHandler(),
    LangChainTracer(project_name="demo-project")
]

# ============================================================
# 步骤2：创建带回调的LLM
# ============================================================
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    streaming=True,  # 必须启用streaming
    callbacks=callbacks
)

# ============================================================
# 步骤3：定义链
# ============================================================
prompt = ChatPromptTemplate.from_template("写一篇关于{topic}的短文，100字左右。")
chain = prompt | llm

# ============================================================
# 步骤4：流式调用
# ============================================================
# 流式输出会触发callbacks的on_llm_new_token事件
print("正在生成内容...")
result = chain.invoke({"topic": "人工智能的未来"})

# ============================================================
# 步骤5：在LangSmith查看追踪
# ============================================================
# 访问 https://smith.langchain.com
# 可以看到：
# - 完整的调用链
# - 每个步骤的输入输出
# - Token使用量和延迟
# - 错误和异常信息
print(f"\n\n完整输出：{result.content}")
