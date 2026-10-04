"""
DatetimeOutputParser基础用法
展示如何解析日期时间格式的LLM输出
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import DatetimeOutputParser
from datetime import datetime

# ============================================================
# 创建DatetimeOutputParser
# ============================================================
# 可以指定输出格式（但实际返回的是datetime对象）
parser = DatetimeOutputParser()

print("格式说明：")
print(parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建Prompt和链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "从以下文本中提取日期时间信息。\n\n"
    "文本：{text}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 执行并解析
# ============================================================
texts = [
    "会议安排在2024年3月15日下午3点",
    "请于2024-12-25完成项目交付",
    "元旦是2025年1月1日",
    "下周三是2024年1月10日"
]

for text in texts:
    try:
        result = chain.invoke({"text": text})
        print(f"输入: {text}")
        print(f"解析: {result}")
        print(f"类型: {type(result)}")
        print(f"格式化: {result.strftime('%Y年%m月%d日 %H:%M')}")
        print("-" * 40)
    except Exception as e:
        print(f"解析失败: {e}")
        print("-" * 40)
