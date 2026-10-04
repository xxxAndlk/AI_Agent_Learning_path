from langchain_core.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

# 定义输入参数模式
class SearchInput(BaseModel):
    query: str = Field(description="搜索查询关键词")
    max_results: int = Field(default=5, description="最大返回结果数")

class WebSearchTool(BaseTool):
    """网络搜索工具"""
    
    name: str = "web_search"
    description: str = "用于搜索互联网信息，获取最新数据和新闻"
    args_schema: Type[BaseModel] = SearchInput
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """同步执行搜索"""
        # 实际实现中这里调用搜索API
        results = []
        for i in range(min(max_results, 3)):
            results.append(f"结果{i+1}: {query}相关信息...")
        return "\n".join(results)
    
    async def _arun(self, query: str, max_results: int = 5) -> str:
        """异步执行搜索"""
        # 异步版本的实现
        results = []
        for i in range(min(max_results, 3)):
            results.append(f"结果{i+1}: {query}相关信息(异步)...")
        return "\n".join(results)

# 使用自定义工具
search_tool = WebSearchTool()
result = search_tool.invoke({"query": "Python教程", "max_results": 3})
print(result)
