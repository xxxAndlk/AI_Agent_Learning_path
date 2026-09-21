"""
JsonOutputParser处理复杂JSON
展示嵌套结构和数组的处理
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# ============================================================
# 创建解析器
# ============================================================
parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_template(
    "分析以下电商订单数据，提取结构化信息。\n\n"
    "订单文本：{order_text}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 复杂订单数据
# ============================================================
order_text = """
订单编号：ORD-2024-001234
客户：张三
下单时间：2024-01-15 14:30:00
订单状态：已完成

商品列表：
1. iPhone 15 Pro 256GB 深空灰 - 1台 - 8999元
2. Apple MagSafe充电器 - 2个 - 398元
3. AirPods Pro 第二代 - 1副 - 1899元

配送地址：
  省份：北京市
  城市：北京市
  区县：朝阳区
  街道：建国路88号
  邮编：100020

支付信息：
  支付方式：支付宝
  支付时间：2024-01-15 14:32:00
  订单金额：11296元
  优惠金额：-296元
  实付金额：11000元
"""

result = chain.invoke({"order_text": order_text})

print("解析结果：")
print("-" * 40)

# 解析订单基本信息
print(f"订单编号: {result.get('订单编号')}")
print(f"客户: {result.get('客户')}")
print(f"订单状态: {result.get('订单状态')}")

# 解析商品列表（数组）
print("\n商品列表:")
items = result.get('商品列表', [])
for item in items:
    print(f"  - {item.get('名称')} x {item.get('数量')} = {item.get('小计')}元")

# 解析配送地址（嵌套对象）
print("\n配送地址:")
address = result.get('配送地址', {})
print(f"  {address.get('省份')} {address.get('城市')} {address.get('区县')}")
print(f"  {address.get('街道')} {address.get('邮编')}")

# 解析支付信息（嵌套对象）
print("\n支付信息:")
payment = result.get('支付信息', {})
print(f"  支付方式: {payment.get('支付方式')}")
print(f"  实付金额: {payment.get('实付金额')}")
