"""
输入映射与转换详解
展示数据如何在管道中流动和转换
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

llm = ChatOpenAI()

# ============================================================
# 简单映射：字典输入
# ============================================================

# 最常见的模式：使用字典作为输入
# 字典的键对应prompt模板中的变量名
simple_prompt = ChatPromptTemplate.from_template("你好，{name}，今天是{day}")
simple_chain = simple_prompt | llm | StrOutputParser()

# 输入字典的键必须匹配模板中的变量
result = simple_chain.invoke({"name": "张三", "day": "星期一"})
print(f"简单映射结果: {result}")

# ============================================================
# 复杂映射：使用函数构建输入
# ============================================================

# 有时候需要从输入中提取或转换数据
# 可以使用函数作为"适配器"

def extract_question_only(inputs):
    """从复杂输入中提取问题"""
    return {"question": inputs.get("question", inputs.get("q", ""))}

complex_prompt = ChatPromptTemplate.from_template("回答这个问题：{question}")
complex_chain = (
    RunnableLambda(extract_question_only)
    | complex_prompt
    | llm
    | StrOutputParser()
)

# 支持多种输入格式
result1 = complex_chain.invoke({"question": "什么是AI"})
result2 = complex_chain.invoke({"q": "什么是AI"})  # 使用不同的键
print(f"复杂映射结果: {result1}")

# ============================================================
# 并行输入映射
# ============================================================

# 使用字典语法可以并行准备多个输入
# 每个键对应一个处理分支
def get_context():
    """模拟获取上下文"""
    return "人工智能是计算机科学的一个分支"

def get_question():
    """模拟获取问题"""
    return "什么是人工智能？"

# 使用字典提供多个并行的数据源
# 左边字典的每个值可以是Runnable或普通值
parallel_input_chain = {
    "context": RunnableLambda(lambda x: get_context()),
    "question": RunnableLambda(lambda x: get_question())
} | ChatPromptTemplate.from_template(
    "上下文：{context}\n问题：{question}"
) | llm | StrOutputParser()

result = parallel_input_chain.invoke({})
print(f"并行输入结果: {result[:50]}...")
