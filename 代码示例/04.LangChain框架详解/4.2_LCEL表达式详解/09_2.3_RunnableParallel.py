"""
RunnableParallel合并多数据源示例
"""
from langchain_core.runnables import RunnableParallel

# 模拟从不同知识库检索
def retrieve_from_database(query):
    """模拟从数据库检索"""
    time.sleep(0.5)  # 模拟延迟
    return f"数据库结果: 关于{query}的信息..."

def retrieve_from_docs(query):
    """模拟从文档检索"""
    time.sleep(0.5)  # 模拟延迟
    return f"文档结果: 关于{query}的文档..."

def retrieve_from_web(query):
    """模拟从网络检索"""
    time.sleep(0.5)  # 模拟延迟
    return f"网络结果: 关于{query}的最新信息..."

# 合并多个检索结果
retriever = RunnableParallel(
    db=RunnableLambda(lambda x: retrieve_from_database(x["query"])),
    docs=RunnableLambda(lambda x: retrieve_from_docs(x["query"])),
    web=RunnableLambda(lambda x: retrieve_from_web(x["query"]))
)

# 一次查询，同时获取三个来源的结果
result = retriever.invoke({"query": "Python教程"})
print(result["db"])
print(result["docs"])
print(result["web"])
