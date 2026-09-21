"""
输出模式与验证
确保LLM输出符合预期格式
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field, validator
from typing import List
import json

llm = ChatOpenAI()

# ============================================================
# 方式1：使用JSON解析器
# ============================================================

# JsonOutputParser自动尝试将LLM输出解析为JSON
# 如果解析失败，会抛出OutputParserException
json_parser = JsonOutputParser()

json_prompt = ChatPromptTemplate.from_template(
    "列出3个{topic}的优点，以JSON数组格式返回"
)
json_chain = json_prompt | llm | json_parser

result = json_chain.invoke({"topic": "远程工作"})
print(f"JSON解析结果: {result}")
print(f"类型: {type(result)}")

# ============================================================
# 方式2：使用Pydantic解析器
# ============================================================

# 定义期望的数据模型
class ToolDefinition(BaseModel):
    """工具定义"""
    name: str = Field(description="工具名称")
    description: str = Field(description="工具功能描述")
    parameters: List[str] = Field(description="参数列表")

class ToolsResponse(BaseModel):
    """工具列表响应"""
    tools: List[ToolDefinition] = Field(description="工具列表")

# 创建Pydantic解析器
pydantic_parser = PydanticOutputParser(pydantic_object=ToolsResponse)

# 自动在prompt中添加格式说明
tools_prompt = ChatPromptTemplate.from_template(
    "定义3个编程工具的信息\n{format_instructions}"
)
# 注意：需要将解析器的格式说明注入到prompt中
tools_prompt_with_format = tools_prompt.partial(
    format_instructions=pydantic_parser.get_format_instructions()
)

tools_chain = tools_prompt_with_format | llm | pydantic_parser

result = tools_chain.invoke({})
print(f"Pydantic解析结果: {result}")
print(f"工具数量: {len(result.tools)}")
print(f"第一个工具: {result.tools[0].name}")
