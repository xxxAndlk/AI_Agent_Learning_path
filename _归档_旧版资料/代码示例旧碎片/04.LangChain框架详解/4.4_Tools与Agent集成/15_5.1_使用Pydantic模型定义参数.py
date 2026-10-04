from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

class Priority(str, Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskInput(BaseModel):
    """任务创建输入参数"""
    title: str = Field(min_length=1, max_length=200, description="任务标题")
    description: str = Field(default="", description="任务详细描述")
    priority: Priority = Field(default=Priority.MEDIUM, description="任务优先级")
    tags: List[str] = Field(default_factory=list, description="任务标签")
    due_date: Optional[str] = Field(default=None, description="截止日期 YYYY-MM-DD")
    estimated_hours: Optional[float] = Field(default=None, ge=0, le=24, description="预计耗时")
    
    @validator('due_date')
    def validate_date(cls, v):
        if v:
            from datetime import datetime
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError('日期格式必须是 YYYY-MM-DD')
        return v

@tool
def create_task(input: TaskInput) -> str:
    """创建新任务"""
    task_info = f"""
任务创建成功！
标题: {input.title}
描述: {input.description or '无'}
优先级: {input.priority.value}
标签: {', '.join(input.tags) if input.tags else '无'}
截止日期: {input.due_date or '未设置'}
预计耗时: {input.estimated_hours}h
"""
    return task_info

# 使用工具
result = create_task.invoke({
    "title": "完成项目文档",
    "description": "编写API文档和使用说明",
    "priority": "high",
    "tags": ["文档", "重要"],
    "due_date": "2024-12-31",
    "estimated_hours": 8.5
})
print(result)
