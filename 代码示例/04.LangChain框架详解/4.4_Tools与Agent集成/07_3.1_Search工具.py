from langchain_community.tools import ArxivQueryRun

arxiv_tool = ArxivQueryRun()

# 搜索学术论文
result = arxiv_tool.invoke("machine learning transformers")
print(result)
