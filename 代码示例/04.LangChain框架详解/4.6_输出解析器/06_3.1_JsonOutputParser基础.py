"""
JsonOutputParser基础用法
展示如何解析JSON格式的LLM输出
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# ============================================================
# 创建JsonOutputParser
# ============================================================
# JsonOutputParser不需要额外参数
# 它会自动尝试从LLM输出中提取JSON数据
parser = JsonOutputParser()

print("格式说明：")
print(parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建Prompt和链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "提取以下文本中的配置信息。\n\n"
    "文本：{text}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 执行并解析
# ============================================================
text = """
服务器配置如下：
应用名称：MyApp
版本：1.0.0
环境：生产
端口：8080
启用缓存：true
最大连接数：100
可选功能：["日志", "监控", "告警"]
"""

result = chain.invoke({"text": text})

print("解析结果：")
print(f"类型: {type(result)}")
print(f"内容: {result}")
print()

# 访问各个字段
print("字段访问：")
print(f"应用名称: {result.get('应用名称')}")
print(f"版本: {result.get('版本')}")
print(f"启用缓存: {result.get('启用缓存')}")
print(f"可选功能: {result.get('可选功能')}")
