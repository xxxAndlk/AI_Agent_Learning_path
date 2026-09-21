from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from langchain_core.tools import tool

class Address(BaseModel):
    """地址信息"""
    street: str = Field(description="街道")
    city: str = Field(description="城市")
    country: str = Field(default="中国", description="国家")

class Person(BaseModel):
    """人物信息"""
    name: str = Field(description="姓名")
    age: int = Field(ge=0, le=150, description="年龄")
    email: Optional[str] = Field(default=None, description="邮箱")
    address: Optional[Address] = Field(default=None, description="地址")

class TeamInput(BaseModel):
    """团队输入参数"""
    team_name: str = Field(description="团队名称")
    members: List[Person] = Field(description="团队成员列表")
    tags: List[str] = Field(default_factory=list, description="团队标签")

@tool
def create_team(input: TeamInput) -> str:
    """创建团队"""
    result = f"团队 '{input.team_name}' 创建成功！\n"
    result += f"标签: {', '.join(input.tags) if input.tags else '无'}\n"
    result += f"成员数量: {len(input.members)}\n\n"
    
    for i, member in enumerate(input.members, 1):
        result += f"成员{i}: {member.name}, {member.age}岁"
        if member.email:
            result += f", {member.email}"
        if member.address:
            result += f", {member.address.city}"
        result += "\n"
    
    return result

# 调用带复杂参数的Tool
result = create_team.invoke({
    "team_name": "AI研发团队",
    "tags": ["研发", "人工智能"],
    "members": [
        {
            "name": "张三",
            "age": 30,
            "email": "zhangsan@example.com",
            "address": {
                "street": "科技路100号",
                "city": "北京"
            }
        },
        {
            "name": "李四",
            "age": 28,
            "address": {
                "street": "创新街50号",
                "city": "上海"
            }
        }
    ]
})
print(result)
