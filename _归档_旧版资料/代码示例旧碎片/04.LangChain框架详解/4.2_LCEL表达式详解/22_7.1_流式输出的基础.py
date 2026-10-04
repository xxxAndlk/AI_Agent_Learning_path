"""
LCEL流式输出基础示例
展示如何获取LLM的实时输出
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建支持流式的LLM
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    streaming=True,  # 关键：启用流式
    callbacks=[]  # 可选：添加回调处理流出的内容
)

# 创建链
chain = (
    ChatPromptTemplate.from_template("写一首关于{topic}的诗")
    | llm
    | StrOutputParser()
)

# ============================================================
# stream方法：同步流式
# ============================================================

print("同步流式输出：")
print("-" * 40)
for chunk in chain.stream({"topic": "春天"}):
    # chunk是每次LLM返回的新内容
    # 可以实时打印或发送到前端
    print(chunk, end="", flush=True)
print("\n" + "-" * 40)
