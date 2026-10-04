"""
XmlOutputParser处理复杂XML
展示属性、嵌套元素和数组的处理
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import XmlOutputParser

# ============================================================
# 创建解析器
# ============================================================
parser = XmlOutputParser()

prompt = ChatPromptTemplate.from_template(
    "将以下图书目录信息转换为XML格式。\n\n"
    "目录描述：{catalog_info}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 复杂目录数据
# ============================================================
catalog_info = """
图书馆目录包含以下图书：

技术类：
- 《Python编程：从入门到实践》
  作者：Eric Matthes
  ISBN：978-7-115-42847-0
  价格：89元
  
- 《算法导论》
  作者：Thomas H. Cormen
  ISBN：978-7-111-42193-0
  价格：128元

文学类：
- 《活着》
  作者：余华
  ISBN：978-7-5399-58452-5
  定价：35元
"""

result = chain.invoke({"catalog_info": catalog_info})

print("解析结果：")
print("-" * 40)

# 遍历结构
def print_xml_structure(data, indent=0):
    """递归打印XML解析结果"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key.startswith('@'):  # 属性
                print(f"{'  ' * indent}属性 {key}: {value}")
            elif key == '#text':
                print(f"{'  ' * indent}文本: {value}")
            else:
                print(f"{'  ' * indent}标签 <{key}>:")
                print_xml_structure(value, indent + 1)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{'  ' * indent}[{i}]:")
            print_xml_structure(item, indent + 1)
    else:
        print(f"{'  ' * indent}值: {data}")

print_xml_structure(result)
