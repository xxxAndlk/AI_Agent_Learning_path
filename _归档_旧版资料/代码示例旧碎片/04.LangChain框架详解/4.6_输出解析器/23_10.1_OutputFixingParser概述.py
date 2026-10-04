"""
OutputFixingParser基础用法
展示如何使用自动修复功能处理解析错误
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import (
    JsonOutputParser,
    OutputFixingParser,
    PydanticOutputParser
)
from pydantic import BaseModel, Field

# ============================================================
# 定义目标数据模型
# ============================================================
class UserProfile(BaseModel):
    """用户资料模型"""
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱地址")
    age: int = Field(description="年龄")
    city: str = Field(description="城市")

# ============================================================
# 创建主解析器和修复解析器
# ============================================================
# 主解析器
base_parser = PydanticOutputParser(pydantic_object=UserProfile)

# 修复解析器
# 需要一个单独的LLM来处理修复逻辑
fixing_llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
fixing_parser = OutputFixingParser(
    parser=base_parser,
    llm=fixing_llm,
    max_retries=3  # 最大重试次数
)

print("修复解析器配置完成")
print("=" * 50)

# ============================================================
# 测试解析错误输出
# ============================================================
# 模拟一个有格式问题的输出
problematic_outputs = [
    # 缺少引号
    """{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "age": "30",
  "city": "北京"
}""",
    
    # 额外的文本
    """以下是用户信息：
{"username": "lisi", "email": "lisi@example.com", "age": 25, "city": "上海"}""",
    
    # 字段缺失
    """{"username": "wangwu", "email": "wangwu@example.com"}""",
    
    # 类型错误
    """{
  "username": "zhaoliu",
  "email": "zhaoliu@example.com",
  "age": "三十",
  "city": "深圳"
}"""
]

prompt = ChatPromptTemplate.from_template(
    "提取用户信息：{text}\n\n{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

# 使用修复解析器的链
chain = prompt | llm | fixing_parser

for i, text in enumerate(problematic_outputs, 1):
    print(f"\n测试 {i}:")
    print(f"输入文本: {text[:50]}...")
    
    try:
        # 模拟通过LLM获取这个有问题的输出
        # 在实际使用中，LLM会直接生成这个输出
        # 这里我们直接调用parse方法测试
        result = fixing_parser.parse(text)
        print(f"修复后解析成功: {result.username}, {result.age}岁, {result.city}")
    except Exception as e:
        print(f"修复失败: {e}")
