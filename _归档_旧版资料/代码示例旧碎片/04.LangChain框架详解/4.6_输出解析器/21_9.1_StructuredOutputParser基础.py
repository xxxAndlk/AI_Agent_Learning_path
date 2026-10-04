"""
StructuredOutputParser基础用法
展示如何通过字典定义输出结构
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StructuredOutputParser

# ============================================================
# 定义输出结构
# ============================================================
# 通过字典定义期望的输出字段
response_schemas = [
    {
        "name": "question",  # 字段名称
        "description": "用户提出的问题",  # 字段描述
        "type": "string"  # 字段类型
    },
    {
        "name": "answer",
        "description": "针对问题的回答",
        "type": "string"
    },
    {
        "name": "confidence",
        "description": "回答的置信度，0-1之间的浮点数",
        "type": "float"
    },
    {
        "name": "sources",
        "description": "回答依据的来源列表",
        "type": "list"
    }
]

# ============================================================
# 创建StructuredOutputParser
# ============================================================
parser = StructuredOutputParser.from_response_schemas(response_schemas)

print("格式说明：")
print(parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建Prompt和链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "根据以下上下文回答用户问题。\n\n"
    "上下文：{context}\n\n"
    "问题：{question}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 执行并解析
# ============================================================
context = """
Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。
Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
Python的哲学强调代码的可读性和简洁的语法。
"""

question = "Python是谁创建的？"

result = chain.invoke({"context": context, "question": question})

print("解析结果：")
print(f"问题: {result.get('question')}")
print(f"回答: {result.get('answer')}")
print(f"置信度: {result.get('confidence')}")
print(f"来源: {result.get('sources')}")
