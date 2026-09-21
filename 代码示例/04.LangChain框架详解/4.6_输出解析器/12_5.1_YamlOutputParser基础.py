"""
YamlOutputParser基础用法
展示如何解析YAML格式的LLM输出
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import YamlOutputParser

# ============================================================
# 创建YamlOutputParser
# ============================================================
parser = YamlOutputParser()

print("格式说明：")
print(parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建Prompt和链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "将以下应用配置转换为YAML格式。\n\n"
    "配置信息：{config_text}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 执行并解析
# ============================================================
config_text = """
应用名称：WebApp
版本：1.0.0
数据库：
  主机：localhost
  端口：5432
  名称：myapp_db
  用户：admin
缓存：
  类型：Redis
  主机：localhost
  端口：6379
日志级别：INFO
启用特性：[认证, 统计, 告警]
"""

result = chain.invoke({"config_text": config_text})

print("解析结果：")
print(f"类型: {type(result)}")
print()

# 访问数据
print("应用配置：")
print(f"  应用名称: {result.get('应用名称')}")
print(f"  版本: {result.get('版本')}")
print()

# 嵌套对象
database = result.get('数据库', {})
print(f"数据库配置：")
print(f"  主机: {database.get('主机')}")
print(f"  端口: {database.get('端口')}")
print(f"  数据库名: {database.get('名称')}")

# 数组
features = result.get('启用特性', [])
print(f"\n启用的特性: {features}")
