"""
解析器选择指南
根据不同场景推荐合适的解析器
"""

# ============================================================
# 场景1：需要强类型验证 -> PydanticOutputParser
# ============================================================
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    id: int = Field(description="用户ID")
    name: str = Field(description="用户名")
    email: str = Field(description="邮箱")
    role: str = Field(description="角色")

# 适合：API返回、数据库记录、业务对象

# ============================================================
# 场景2：简单JSON -> JsonOutputParser
# ============================================================
from langchain_core.output_parsers import JsonOutputParser

# 适合：配置解析、简单数据结构、动态字段

# ============================================================
# 场景3：需要自动修复 -> OutputFixingParser + 任意解析器
# ============================================================
from langchain_core.output_parsers import OutputFixingParser

# 适合：用户输入解析、不稳定输出、容错要求高

# ============================================================
# 场景4：枚举限制 -> EnumOutputParser
# ============================================================
from langchain_core.output_parsers import EnumOutputParser
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

# 适合：状态机、选项限制、分类任务
