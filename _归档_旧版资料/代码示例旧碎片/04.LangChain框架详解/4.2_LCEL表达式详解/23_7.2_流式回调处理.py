"""
流式回调处理示例
展示如何使用回调自定义流式行为
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import json

# 自定义回调处理器
class MyStreamHandler(BaseCallbackHandler):
    """自定义流式回调处理器"""
    
    def __init__(self):
        self.tokens = []
    
    def on_llm_new_token(self, token: str, **kwargs):
        """每次收到新token时调用"""
        self.tokens.append(token)
        # 可以在这里实现自定义逻辑：
        # - 实时发送到WebSocket
        # - 保存到数据库
        # - 进行实时分析
        print(f"收到token: {token}", end="", flush=True)
    
    def get_full_response(self) -> str:
        """获取完整响应"""
        return "".join(self.tokens)

# 创建带回调的LLM
handler = MyStreamHandler()
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    streaming=True,
    callbacks=[handler]  # 注入回调
)

chain = (
    ChatPromptTemplate.from_template("用三句话解释{topic}")
    | llm
)

print("\n使用回调的流式输出：")
result = chain.invoke({"topic": "量子纠缠"})
print(f"\n\n完整响应: {result}")
print(f"Token数量: {len(handler.tokens)}")
