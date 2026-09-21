"""
LCEL类型提示与模式定义
展示如何利用类型系统提高代码质量
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from typing import Optional

llm = ChatOpenAI()

# ============================================================
# 查看组件的输入输出模式
# ============================================================

prompt = ChatPromptTemplate.from_template("翻译以下内容为中文：{text}")

# input_schema描述组件期望的输入格式
# 对于prompt，这里是Dict[str, Any]，text是必需的键
print(f"Prompt输入模式: {prompt.input_schema}")
print(f"Prompt输出模式: {prompt.output_schema}")

# 添加更多变量后，模式会相应更新
prompt_with_optional = ChatPromptTemplate.from_messages([
    ("system", "你是一个翻译助手"),
    ("human", "将以下{text}翻译为{language}")
])

# language有默认值，所以是可选的
schema = prompt_with_optional.input_schema
print(f"带默认值Prompt的输入模式: {schema}")
print(f"required_fields: {schema.schema().get('required', [])}")

# ============================================================
# 自定义输出模式
# ============================================================

# 使用Pydantic模型定义输出结构
class AnswerWithConfidence(BaseModel):
    """带有置信度的答案"""
    answer: str = Field(description="问题的答案")
    confidence: float = Field(description="置信度，0-1之间")
    sources: Optional[list[str]] = Field(default_factory=list, description="参考来源")

# 创建支持结构化输出的链
structured_llm = llm.with_structured_output(AnswerWithConfidence)

# 这种方式下，LLM的输出会被自动解析为Pydantic对象
# 如果解析失败，会抛出ValidationError
chain = (
    ChatPromptTemplate.from_template("回答以下问题：{question}")
    | structured_llm
)

result = chain.invoke({"question": "太阳系最大的行星是什么？"})
print(f"答案: {result.answer}")
print(f"置信度: {result.confidence}")
print(f"来源: {result.sources}")
