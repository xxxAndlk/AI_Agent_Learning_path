from pydantic import BaseModel, Field
from typing import Optional, Literal
from langchain_core.tools import Tool

class SearchImageInput(BaseModel):
    """图片搜索参数"""
    query: str = Field(description="搜索关键词")
    source: Literal["google", "bing", "unsplash"] = Field(
        default="google",
        description="图片来源"
    )
    count: int = Field(
        default=10,
        ge=1,
        le=50,
        description="返回图片数量"
    )
    safe_search: bool = Field(
        default=True,
        description="是否启用安全搜索"
    )

def search_images_func(query: str, source: str = "google", 
                       count: int = 10, safe_search: bool = True) -> str:
    """搜索图片"""
    return f"从 {source} 搜索 '{query}'，返回 {count} 张图片，安全搜索: {safe_search}"

# 创建带args_schema的Tool
image_search_tool = Tool(
    name="image_search",
    func=search_images_func,
    description="搜索图片，支持多个来源",
    args_schema=SearchImageInput
)

# 调用
result = image_search_tool.invoke({
    "query": "美丽的日出",
    "source": "unsplash",
    "count": 5,
    "safe_search": True
})
print(result)
