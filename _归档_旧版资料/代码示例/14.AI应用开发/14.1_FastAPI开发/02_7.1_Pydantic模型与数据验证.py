from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")
    full_name: Optional[str] = Field(None, description="真实姓名")


class UserCreate(UserBase):
    """用户创建请求模型"""
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """验证两次密码是否一致"""
        if "password" in values and v != values["password"]:
            raise ValueError("两次输入的密码不一致")
        return v
    
    @validator("password")
    def password_strength(cls, v):
        """验证密码强度"""
        if not any(c.isupper() for c in v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含至少一个数字")
        return v


class UserResponse(UserBase):
    """用户响应模型（不包含敏感信息）"""
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        """Pydantic配置"""
        from_attributes = True  # 允许从ORM模型读取属性


class UserUpdate(BaseModel):
    """用户更新模型（所有字段可选）"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class PaginationParams:
    """分页参数依赖"""
    def __init__(self, page: int = 1, page_size: int = 20):
        if page < 1:
            raise ValueError("页码必须大于0")
        if page_size < 1 or page_size > 100:
            raise ValueError("每页数量必须在1-100之间")
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any] = Field(..., description="数据列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
