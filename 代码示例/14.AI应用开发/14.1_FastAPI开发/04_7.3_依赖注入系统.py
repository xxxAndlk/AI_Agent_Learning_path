from fastapi import Depends, Header, Cookie, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
import jwt
from datetime import datetime, timedelta


# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """从Token获取当前用户（依赖注入）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    # 从数据库获取用户
    for user in fake_users_db.values():
        if user["username"] == username:
            return UserResponse(**user)
    raise credentials_exception


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """获取当前激活的用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """获取当前管理员用户"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


# 可选的依赖项
async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[UserResponse]:
    """获取可选的用户（未登录时返回None）"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    try:
        return await get_current_user(token)
    except HTTPException:
        return None


# 带缓存的依赖项
from functools import lru_cache


@lru_cache()
def get_settings():
    """获取应用配置（带缓存）"""
    return {"debug": True, "api_version": "v1"}


# 类的依赖项
class QueryParams:
    def __init__(self, q: str = "", page: int = 1):
        self.q = q
        self.page = page


def get_query_params(
    q: str = Query("", description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码")
) -> QueryParams:
    """从查询参数创建对象"""
    return QueryParams(q=q, page=page)


@api_router.get("/search")
async def search(
    params: QueryParams = Depends(get_query_params),
    current_user: Optional[UserResponse] = Depends(get_optional_user)
):
    """搜索接口（展示依赖注入）"""
    return {
        "query": params.q,
        "page": params.page,
        "user": current_user.username if current_user else "匿名用户"
    }


# 条件依赖
async def get_database_with_condition(
    x_feature_flag: str = Header(None)
):
    """条件依赖示例"""
    if x_feature_flag == "enabled":
        return "feature_enabled_db"
    return "default_db"


@api_router.get("/feature-flagged")
async def feature_flagged_route(
    db: str = Depends(get_database_with_condition)
):
    return {"database": db, "feature": "active"}
