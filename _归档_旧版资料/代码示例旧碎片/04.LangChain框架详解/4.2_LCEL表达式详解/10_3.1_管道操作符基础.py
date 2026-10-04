"""
管道操作符基础用法
展示从简单到复杂的管道组合
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser

llm = ChatOpenAI()

# ============================================================
# 基础管道：单步组合
# ============================================================

# 最简单的管道：prompt + llm
# 输入字典 -> prompt模板 -> LLM调用 -> AIMessage
simple_chain = ChatPromptTemplate.from_template("你好，我是{name}") | llm
result = simple_chain.invoke({"name": "张三"})
print(f"基础管道结果: {result.content}")

# ============================================================
# 扩展管道：添加输出解析器
# ============================================================

# 添加StrOutputParser将AIMessage转为字符串
chain_with_parser = (
    ChatPromptTemplate.from_template("用一句话介绍{topic}")
    | llm
    | StrOutputParser()
)
result = chain_with_parser.invoke({"topic": "人工智能"})
print(f"带解析器的管道: {result}")

# ============================================================
# 完整管道：多步骤处理
# ============================================================

# 完整管道通常包含：输入转换 -> prompt -> llm -> 输出解析
full_chain = (
    ChatPromptTemplate.from_template("列出{count}个关于{topic}的优点")
    | llm
    | StrOutputParser()
    | (lambda x: x.upper())  # 添加自定义转换
)
result = full_chain.invoke({"count": 3, "topic": "学习编程"})
print(f"完整管道结果:\n{result}")
