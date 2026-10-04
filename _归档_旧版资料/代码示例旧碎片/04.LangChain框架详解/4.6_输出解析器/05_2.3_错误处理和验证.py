"""
PydanticOutputParser错误处理
展示如何处理验证错误和解析失败
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# ============================================================
# 定义需要严格验证的模型
# ============================================================
class ProductInfo(BaseModel):
    """产品信息模型"""
    name: str = Field(description="产品名称")
    price: float = Field(description="产品价格，必须为正数")
    category: str = Field(description="产品类别")
    in_stock: bool = Field(description="是否有库存")

# ============================================================
# 创建解析器
# ============================================================
parser = PydanticOutputParser(pydantic_object=ProductInfo)

prompt = ChatPromptTemplate.from_template(
    "提取产品信息：{description}\n\n{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 测试用例1：正常数据
# ============================================================
print("测试1：正常数据")
try:
    result = chain.invoke({
        "description": "iPhone 15 Pro Max 手机，价格9999元，属于电子产品，有库存"
    })
    print(f"成功: {result.name}, 价格: {result.price}")
except ValidationError as e:
    print(f"验证错误: {e}")

print("-" * 30)

# ============================================================
# 测试用例2：无效价格（负数）
# ============================================================
print("测试2：无效价格")
# 模拟一个包含无效数据的响应
test_response = """
```json
{
  "name": "某个产品",
  "price": -100,
  "category": "测试类别",
  "in_stock": true
}
```
"""
try:
    result = parser.parse(test_response)
    print(f"成功: {result.name}")
except ValidationError as e:
    print(f"验证错误（预期）: {e.error_count}个错误")
    for error in e.errors():
        print(f"  - 字段: {error['loc']}, 错误: {error['msg']}")

print("-" * 30)

# ============================================================
# 测试用例3：缺失必需字段
# ============================================================
print("测试3：缺失字段")
test_response = """
```json
{
  "name": "只有名称的产品"
}
```
"""
try:
    result = parser.parse(test_response)
    print(f"成功: {result.name}")
except ValidationError as e:
    print(f"验证错误（预期）: {e.error_count}个错误")
    for error in e.errors():
        print(f"  - 字段: {error['loc']}, 错误: {error['msg']}")

print("-" * 30)

# ============================================================
# 测试用例4：完全无效的输出
# ============================================================
print("测试4：无效输出格式")
test_response = "这是一段完全不包含JSON的文字"
try:
    result = parser.parse(test_response)
    print(f"成功: {result}")
except Exception as e:
    print(f"解析错误（预期）: {type(e).__name__}: {e}")
