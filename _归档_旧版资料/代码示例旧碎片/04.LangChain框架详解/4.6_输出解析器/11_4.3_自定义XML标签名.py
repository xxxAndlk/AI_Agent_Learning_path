"""
XmlOutputParser自定义标签
展示如何配置标签名称
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import XmlOutputParser

# ============================================================
# 自定义标签名称
# ============================================================
# root_key: 根元素的名称
# item_key: 列表中每个元素的名称
parser = XmlOutputParser(
    root_key="response",
    item_key="item"
)

prompt = ChatPromptTemplate.from_template(
    "将以下数据转换为XML：{data}\n\n{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

result = chain.invoke({"data": "苹果、香蕉、橙子"})
print("自定义标签解析结果：")
print(result)
