from langchain_core.tools import tool

# 方法1: 使用工具描述明确优先级
@tool
def urgent_handler(query: str) -> str:
    """处理紧急和重要的问题，优先级最高"""
    return "紧急处理"

@tool
def normal_handler(query: str) -> str:
    """处理一般性问题，优先级普通"""
    return "普通处理"

@tool
def background_handler(query: str) -> str:
    """处理耗时的后台任务，优先级最低"""
    return "后台处理"

priority_tools = [urgent_handler, normal_handler, background_handler]

# 方法2: 将相关工具分组管理
search_tools = [search_docs, search_github, search_stackoverflow]
print(f"搜索工具包: {[t.name for t in search_tools]}")
