from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
import asyncio


# 创建子路由器
api_router = APIRouter(prefix="/api/v1", tags=["API v1"])

# 模拟数据库
fake_users_db = {
    1: {"id": 1, "username": "alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "username": "bob", "email": "bob@example.com", "role": "user"},
}


@api_router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = Query(None, description="按角色筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """获取用户列表（需要认证）"""
    users = list(fake_users_db.values())
    
    if role:
        users = [u for u in users if u.get("role") == role.value]
    
    return users[skip:skip + limit]


@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """获取单个用户详情"""
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    return fake_users_db[user_id]


@api_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """创建新用户（需要管理员权限）"""
    # 检查用户名是否已存在
    for existing_user in fake_users_db.values():
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建新用户
    user_id = max(fake_users_db.keys()) + 1
    new_user = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    fake_users_db[user_id] = new_user
    return new_user


@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """更新用户信息"""
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user_data = fake_users_db[user_id]
    
    # 更新非空字段
    update_data = user_update.dict(exclude_unset=True)
    user_data.update(update_data)
    fake_users_db[user_id] = user_data
    
    return user_data


@api_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """删除用户"""
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    del fake_users_db[user_id]
    return None


# 批量操作路由
@api_router.post("/users/batch", response_model=List[UserResponse])
async def create_users_batch(
    users: List[UserCreate],
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """批量创建用户"""
    created_users = []
    for user in users:
        user_id = max(fake_users_db.keys()) + 1 if fake_users_db else 1
        new_user = {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        fake_users_db[user_id] = new_user
        created_users.append(new_user)
    return created_users
