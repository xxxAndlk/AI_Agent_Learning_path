from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# 创建Wikipedia工具
wiki_api = WikipediaAPIWrapper()
wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api)

# 执行查询
result = wiki_tool.invoke("Python编程语言")
print(result[:500])  # 打印前500字符
