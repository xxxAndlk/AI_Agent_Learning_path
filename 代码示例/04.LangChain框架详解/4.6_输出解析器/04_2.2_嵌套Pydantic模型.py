"""
PydanticOutputParser嵌套模型示例
展示如何处理复杂的层级数据结构
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

# ============================================================
# 定义嵌套的数据模型
# ============================================================

class Address(BaseModel):
    """地址信息"""
    street: str = Field(description="街道地址")
    city: str = Field(description="城市")
    province: str = Field(description="省份")
    zip_code: str = Field(description="邮政编码")

class Company(BaseModel):
    """公司信息"""
    name: str = Field(description="公司名称")
    position: str = Field(description="职位")
    department: Optional[str] = Field(default=None, description="部门")

class Person(BaseModel):
    """人物完整信息"""
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    email: str = Field(description="邮箱地址")
    phone: Optional[str] = Field(default=None, description="电话号码")
    address: Address = Field(description="地址信息")
    work_experience: List[Company] = Field(description="工作经历")
    skills: List[str] = Field(description="技能列表")

# ============================================================
# 创建解析器
# ============================================================
parser = PydanticOutputParser(pydantic_object=Person)

print("格式说明：")
print(parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "请从以下文本中提取人物信息。\n\n"
    "文本内容：{text}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 测试解析
# ============================================================
text = """
张三，35岁，软件工程师。他住在北京市朝阳区建国路88号，邮编100020。
邮箱是 zhangsan@tech.com，手机号13800138000。
曾在阿里巴巴担任高级开发工程师，在字节跳动担任技术主管。
技能包括Python、Go、Java、微服务架构、云计算等。
"""

result = chain.invoke({"text": text})

# 访问嵌套数据
print(f"姓名: {result.name}")
print(f"年龄: {result.age}")
print(f"邮箱: {result.email}")
print(f"地址: {result.address.city} {result.address.street}")
print(f"工作经历数量: {len(result.work_experience)}")
for i, company in enumerate(result.work_experience, 1):
    print(f"  工作{i}: {company.name} - {company.position}")
print(f"技能: {result.skills}")
