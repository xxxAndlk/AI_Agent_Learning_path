@tool
def search_engine(query: str) -> str:
    """执行搜索引擎查询
    
    Args:
        query: 搜索关键词
        
    Returns:
        搜索结果的摘要文本
    """
    # 这里可以调用真实的搜索API
    return f"关于 '{query}' 的搜索结果..."

# 获取工具的参数模式
print(search_engine.args_schema.schema())
# 输出类似：
# {
#     "type": "object",
#     "properties": {
#         "query": {"type": "string", "description": "执行搜索引擎查询\n\nArgs:\n    query: 搜索关键词\n    \n    Returns:\n        搜索结果的摘要文本"}
#     },
#     "required": ["query"]
# }
