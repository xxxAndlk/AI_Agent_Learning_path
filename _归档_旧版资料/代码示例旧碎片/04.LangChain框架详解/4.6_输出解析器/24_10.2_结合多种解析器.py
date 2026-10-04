"""
OutputFixingParser与不同解析器结合
展示与JsonOutputParser和XML解析器的结合
"""

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import (
    JsonOutputParser,
    XmlOutputParser,
    YamlOutputParser,
    OutputFixingParser
)

# ============================================================
# 创建不同类型的修复解析器
# ============================================================
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

# JSON修复解析器
json_parser = JsonOutputParser()
json_fixer = OutputFixingParser.from_llm(llm, json_parser)

# XML修复解析器
xml_parser = XmlOutputParser()
xml_fixer = OutputFixingParser.from_llm(llm, xml_parser)

# YAML修复解析器
yaml_parser = YamlOutputParser()
yaml_fixer = OutputFixingParser.from_llm(llm, yaml_parser)

# ============================================================
# 测试各种错误格式
# ============================================================
test_cases = [
    ("JSON", json_fixer, '{"name": "test", "value": }'),  # 截断的JSON
    ("XML", xml_fixer, '<item><name>test</item>'),  # 不匹配的标签
    ("YAML", yaml_fixer, 'name: test\nvalue:'),  # 截断的YAML
]

for format_name, parser, bad_input in test_cases:
    print(f"\n测试 {format_name} 解析:")
    print(f"输入: {bad_input}")
    try:
        result = parser.parse(bad_input)
        print(f"修复成功: {result}")
    except Exception as e:
        print(f"仍然失败: {type(e).__name__}: {e}")
