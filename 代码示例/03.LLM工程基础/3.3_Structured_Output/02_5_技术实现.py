from pydantic import BaseModel, Field
from typing import List

class User(BaseModel):
    name: str = Field(description="用户名")
    age: int = Field(description="年龄")
    hobbies: List[str] = Field(description="爱好列表")
