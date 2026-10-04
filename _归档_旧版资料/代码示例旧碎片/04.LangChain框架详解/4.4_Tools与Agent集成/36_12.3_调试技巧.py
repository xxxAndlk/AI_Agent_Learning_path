# 使用 LangSmith 进行调试和追踪（推荐）
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"

# 调试信息通过 LangSmith 平台查看
# 访问 https://smith.langchain.com 查看完整的执行轨迹

# 或者使用回调处理器
from langchain.callbacks import StdOutCallbackHandler

result = agent.invoke(
    {"messages": [{"role": "user", "content": "问题"}]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("结果:", result["messages"][-1].content)
