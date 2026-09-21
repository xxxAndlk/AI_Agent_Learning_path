"""
XmlOutputParser基础用法
展示如何解析XML格式的LLM输出
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import XmlOutputParser

# ============================================================
# 创建XmlOutputParser
# ============================================================
# 可以选择是否返回标签名称
parser = XmlOutputParser()

print("格式说明：")
print(parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建Prompt和链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "将以下人物信息转换为XML格式。\n\n"
    "人物描述：{description}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 执行并解析
# ============================================================
description = "张三，软件工程师，30岁，住在北京市朝阳区，擅长Python和Go语言。"

result = chain.invoke({"description": description})

print("解析结果：")
print(f"类型: {type(result)}")
print(f"内容: {result}")
print()

# 访问各个元素
print("元素访问：")
if 'person' in result:
    person = result['person']
    if isinstance(person, dict):
        print(f"姓名: {person.get('name', {}).get('#text')}")
        print(f"职业: {person.get('profession', {}).get('#text')}")
        print(f"年龄: {person.get('age', {}).get('#text')}")
