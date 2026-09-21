"""
JsonOutputParser与Pydantic结合
先用JsonOutputParser解析JSON，再用Pydantic验证
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, ValidationError
from typing import List

# ============================================================
# 定义Pydantic模型用于二次验证
# ============================================================
class ConfigSchema(BaseModel):
    """配置信息验证模型"""
    app_name: str = Field(alias="应用名称")
    version: str = Field(alias="版本")
    environment: str = Field(alias="环境")
    port: int = Field(alias="端口")
    max_connections: int = Field(alias="最大连接数")
    features: List[str] = Field(alias="可选功能")

    class Config:
        # 允许Pydantic使用别名
        populate_by_name = True

# ============================================================
# 构建链
# ============================================================
json_parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_template(
    "提取配置信息：{text}\n\n{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

# 链：解析JSON -> 验证并转换
chain = prompt | llm | json_parser

# 执行
text = "应用：MyService，版本：2.0.0，生产环境，端口8080，最大连接200，功能有日志和监控"

# 第一步：获取JSON字典
json_dict = chain.invoke({"text": text})
print("原始JSON解析结果：")
print(json_dict)
print()

# 第二步：用Pydantic验证和转换
try:
    config = ConfigSchema.model_validate(json_dict)
    print("验证通过！")
    print(f"应用: {config.app_name}")
    print(f"版本: {config.version}")
    print(f"端口: {config.port}")
except ValidationError as e:
    print(f"验证失败: {e}")
