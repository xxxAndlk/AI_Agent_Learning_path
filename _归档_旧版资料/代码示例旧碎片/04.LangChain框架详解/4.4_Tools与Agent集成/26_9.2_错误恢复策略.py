from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Type, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FallbackInput(BaseModel):
    query: str = Field(description="查询内容")

class FallbackTool(BaseTool):
    """带有降级策略的工具"""
    
    name: str = "fallback_search"
    description: str = "带降级策略的搜索工具"
    args_schema: Type[BaseModel] = FallbackInput
    
    def __init__(self):
        super().__init__()
        self.primary_source = "主数据源"
        self.fallback_source = "备用数据源"
    
    def _run(self, query: str) -> str:
        try:
            # 尝试主数据源
            logger.info(f"使用{self.primary_source}搜索: {query}")
            return self._search_primary(query)
        except Exception as e:
            logger.warning(f"主数据源失败，切换到{self.fallback_source}: {e}")
            try:
                return self._search_fallback(query)
            except Exception as e2:
                logger.error(f"备用数据源也失败: {e2}")
                return f"搜索失败: 所有数据源不可用"
    
    def _search_primary(self, query: str) -> str:
        # 模拟主数据源
        if "error" in query.lower():
            raise ConnectionError("主数据源错误")
        return f"从主数据源返回: {query}的相关结果"
    
    def _search_fallback(self, query: str) -> str:
        # 模拟备用数据源
        return f"从备用数据源返回: {query}的相关结果"

# 测试降级策略
tool = FallbackTool()
print(tool.invoke({"query": "正常查询"}))
print(tool.invoke({"query": "error测试"}))
