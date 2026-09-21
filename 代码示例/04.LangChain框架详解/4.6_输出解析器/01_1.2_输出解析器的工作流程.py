"""
输出解析器工作流程示意图
本示例展示了数据从LLM输出到结构化对象的完整流转过程
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from typing import Optional

# ============================================================
# 步骤1：定义期望的数据模型
# ============================================================
# 使用Pydantic定义输出的数据结构
# 这样可以享受自动验证和类型提示的好处
class UserInfo(BaseModel):
    """用户信息数据模型"""
    name: str           # 用户姓名，必填字段
    age: int            # 年龄，整数类型
    email: Optional[str] = None  # 邮箱，可选字段

# ============================================================
# 步骤2：创建解析器实例
# ============================================================
# JsonOutputParser将LLM输出解析为JSON字典
# 结合Pydantic模型，可以自动验证和转换类型
json_parser = JsonOutputParser(pydantic_object=UserInfo)

# 获取解析器的格式说明，用于自动填充到Prompt中
format_instructions = json_parser.get_format_instructions()
print("格式说明：")
print(format_instructions)
print()

# ============================================================
# 步骤3：创建Prompt模板
# ============================================================
# 模板中包含{format_instructions}占位符
# 解析器会自动填充正确的格式说明
prompt = ChatPromptTemplate.from_template(
    "请根据用户描述提取用户信息。\n\n用户描述：{description}\n\n{format_instructions}"
)

# ============================================================
# 步骤4：创建LLM实例
# ============================================================
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

# ============================================================
# 步骤5：构建LCEL链
# ============================================================
# 使用管道操作符组合组件
# 数据流：description -> prompt -> llm -> json_parser -> UserInfo对象
chain = prompt | llm | json_parser

# ============================================================
# 步骤6：执行并获取结构化输出
# ============================================================
description = "张三是一位30岁的软件工程师，他的邮箱是 zhangsan@company.com"

# invoke返回的是UserInfo类型的对象
result = chain.invoke({"description": description})

print("解析结果：")
print(f"类型: {type(result)}")
print(f"姓名: {result.name}")
print(f"年龄: {result.age}")
print(f"邮箱: {result.email}")
