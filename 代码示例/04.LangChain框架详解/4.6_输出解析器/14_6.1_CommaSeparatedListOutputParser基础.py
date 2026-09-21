"""
CommaSeparatedListOutputParser基础用法
展示如何解析列表格式的LLM输出
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser

# ============================================================
# 创建CommaSeparatedListOutputParser
# ============================================================
parser = CommaSeparatedListOutputParser()

print("格式说明：")
print(parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建Prompt和链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "从以下文本中提取关键技术术语。\n\n"
    "文本：{text}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 执行并解析
# ============================================================
text = """
Python是一种高级编程语言，广泛用于Web开发、数据分析、人工智能等领域。
它支持多种编程范式，包括面向对象、函数式和过程式编程。
Python拥有丰富的标准库和第三方包，如NumPy、Pandas、TensorFlow等。
"""

result = chain.invoke({"text": text})

print("解析结果：")
print(f"类型: {type(result)}")
print(f"长度: {len(result)}")
print(f"内容: {result}")
print()

# 使用解析后的列表
print("提取的术语：")
for i, term in enumerate(result, 1):
    print(f"  {i}. {term}")
