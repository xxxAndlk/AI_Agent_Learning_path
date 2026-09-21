"""
链的复用与组合示例
展示如何构建可复用的链组件
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

llm = ChatOpenAI()

# ============================================================
# 示例1：创建可复用的子链
# ============================================================

# 定义一个通用的翻译子链
translation_prompt = ChatPromptTemplate.from_template(
    "将以下文本翻译为{language}：{text}"
)
translator = translation_prompt | llm | StrOutputParser()

# 可以在多个地方复用这个translator
result1 = translator.invoke({"language": "英语", "text": "你好"})
result2 = translator.invoke({"language": "日语", "text": "你好"})
result3 = translator.invoke({"language": "法语", "text": "你好"})
print(f"英语: {result1}")
print(f"日语: {result2}")
print(f"法语: {result3}")

# ============================================================
# 示例2：组合多个子链
# ============================================================

# 定义子链：问题分析
analyze_prompt = ChatPromptTemplate.from_template(
    "分析这个问题的主要意图：{question}"
)
analyzer = analyze_prompt | llm | StrOutputParser()

# 定义子链：生成答案
answer_prompt = ChatPromptTemplate.from_template(
    "基于以下分析生成答案：\n分析：{analysis}\n问题：{question}"
)
answerer = answer_prompt | llm | StrOutputParser()

# 组合成完整链
# 这里使用RunnablePassthrough来传递原始输入
full_chain = (
    {"analysis": analyzer, "question": RunnablePassthrough()}
    | answerer
)

result = full_chain.invoke("什么是机器学习？")
print(f"完整链结果: {result[:100]}...")

# ============================================================
# 示例3：链的变体
# ============================================================

# 定义基础链
base_prompt = ChatPromptTemplate.from_template("{task}")
base_chain = base_prompt | llm | StrOutputParser()

# 创建变体：添加不同的前缀
def with_context(prefix: str):
    """为链添加上下文前缀"""
    return (
        {"task": RunnableLambda(lambda x: f"{prefix}: {x['task']}")}
        | base_chain
    )

creative_chain = with_context("发挥你的创造力")
formal_chain = with_context("用正式专业的语言")

result1 = creative_chain.invoke({"task": "解释量子计算"})
result2 = formal_chain.invoke({"task": "解释量子计算"})
print(f"创意风格: {result1[:50]}...")
print(f"正式风格: {result2[:50]}...")
