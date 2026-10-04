"""
StructuredOutputParser复杂结构
展示定义嵌套和多层结构的方法
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StructuredOutputParser

# ============================================================
# 定义复杂的产品信息结构
# ============================================================
product_schemas = [
    {
        "name": "product_name",
        "description": "产品名称",
        "type": "string"
    },
    {
        "name": "brand",
        "description": "品牌名称",
        "type": "string"
    },
    {
        "name": "price",
        "description": "产品价格，单位为元",
        "type": "float"
    },
    {
        "name": "specifications",
        "description": "产品规格详情",
        "type": "object",
        "properties": {
            "weight": "重量，单位kg",
            "dimensions": "尺寸，长x宽x高",
            "color": "颜色",
            "material": "材质"
        }
    },
    {
        "name": "features",
        "description": "产品主要特性列表",
        "type": "list"
    },
    {
        "name": "availability",
        "description": "库存状态",
        "type": "string",
        "enum": ["有货", "缺货", "预售"]
    }
]

# ============================================================
# 创建解析器
# ============================================================
parser = StructuredOutputParser.from_response_schemas(product_schemas)

prompt = ChatPromptTemplate.from_template(
    "提取以下产品描述中的详细信息。\n\n"
    "产品描述：{description}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 测试解析
# ============================================================
description = """
iPhone 15 Pro Max 是苹果公司的旗舰智能手机。
机身采用钛金属材质，重量为221g。
尺寸为76.7 x 8.25 x 159.9mm。
提供原色钛金属、蓝色钛金属、白色钛金属和黑色钛金属四种颜色。
支持A17 Pro芯片，配备4800万像素主摄像头。
价格9999元，目前有货。
"""

result = chain.invoke({"description": description})

print("产品信息：")
print(f"名称: {result.get('product_name')}")
print(f"品牌: {result.get('brand')}")
print(f"价格: {result.get('price')}元")

specs = result.get('specifications', {})
print(f"\n规格：")
print(f"  重量: {specs.get('weight')}")
print(f"  尺寸: {specs.get('dimensions')}")
print(f"  颜色: {specs.get('color')}")
print(f"  材质: {specs.get('material')}")

features = result.get('features', [])
print(f"\n特性: {features}")
print(f"库存: {result.get('availability')}")
