"""
EnumOutputParser基础用法
展示如何限制LLM输出为预定义的枚举值
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import EnumOutputParser
from enum import Enum

# ============================================================
# 定义枚举类型
# ============================================================
class Priority(Enum):
    """优先级枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    URGENT = "紧急"

class Status(Enum):
    """状态枚举"""
    PENDING = "待处理"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"

# ============================================================
# 创建EnumOutputParser
# ============================================================
priority_parser = EnumOutputParser(enum=Priority)

print("格式说明：")
print(priority_parser.get_format_instructions())
print("=" * 50)

# ============================================================
# 构建Prompt和链
# ============================================================
prompt = ChatPromptTemplate.from_template(
    "根据以下任务的紧急程度确定优先级。\n\n"
    "任务描述：{task}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | priority_parser

# ============================================================
# 测试不同任务
# ============================================================
tasks = [
    "修复一个导致系统崩溃的严重bug",
    "更新文档中的错别字",
    "添加一个新的用户界面按钮",
    "处理客户投诉"
]

for task in tasks:
    try:
        result = chain.invoke({"task": task})
        print(f"任务: {task}")
        print(f"优先级: {result.name} = {result.value}")
        print("-" * 40)
    except Exception as e:
        print(f"解析失败: {e}")
