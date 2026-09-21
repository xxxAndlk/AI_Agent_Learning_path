class PermissionManager:
    """权限管理器"""
    
    # 权限定义
    PERMISSIONS = {
        "knowledge:read": "读取知识库",
        "knowledge:write": "编辑知识库",
        "user:read": "查看用户",
        "user:write": "管理用户",
        "tool:meeting:book": "预约会议室",
        "tool:email:send": "发送邮件",
        "tool:task:create": "创建任务",
        "audit:read": "查看审计日志",
        "settings:write": "修改系统设置"
    }
    
    # 角色权限映射
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: list(PERMISSIONS.keys()),
        UserRole.HR: [
            "knowledge:read", "user:read", "tool:email:send",
            "hr_policy:read", "audit:read"
        ],
        UserRole.FINANCE: [
            "knowledge:read", "user:read", "finance_query:read",
            "tool:email:send", "audit:read"
        ],
        UserRole.IT: [
            "knowledge:read", "user:read", "tool:email:send",
            "tool:meeting:book", "audit:read"
        ],
        UserRole.EMPLOYEE: [
            "knowledge:read", "tool:meeting:book", "tool:email:send",
            "tool:task:create"
        ],
        UserRole.GUEST: [
            "knowledge:read"
        ]
    }
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self._init_default_users()
    
    def _init_default_users(self):
        """初始化默认用户"""
        default_users = [
            User(
                user_id="admin001",
                username="admin",
                email="admin@company.com",
                role=UserRole.ADMIN,
                department="IT",
                permissions=[]
            ),
            User(
                user_id="hr001",
                username="hr_manager",
                email="hr@company.com",
                role=UserRole.HR,
                department="人力资源",
                permissions=[]
            ),
            User(
                user_id="emp001",
                username="employee",
                email="employee@company.com",
                role=UserRole.EMPLOYEE,
                department="研发",
                permissions=[]
            )
        ]
        
        for user in default_users:
            # 根据角色分配权限
            user.permissions = self.ROLE_PERMISSIONS.get(user.role, [])
            self.users[user.user_id] = user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        # 简化实现，实际应该使用真实数据库和密码哈希
        for user in self.users.values():
            if user.username == username:
                if user.is_active:
                    logger.info(f"用户 {username} 登录成功")
                    return user
                else:
                    logger.warning(f"用户 {username} 账户已被禁用")
        return None
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """检查用户权限"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if user.role == UserRole.ADMIN:
            return True
        
        return permission in user.permissions
    
    def authorize_action(self, user_id: str, action: str) -> bool:
        """授权操作"""
        # 动作到权限的映射
        action_permission_map = {
            "view_knowledge": "knowledge:read",
            "edit_knowledge": "knowledge:write",
            "view_users": "user:read",
            "manage_users": "user:write",
            "book_meeting": "tool:meeting:book",
            "send_email": "tool:email:send",
            "create_task": "tool:task:create",
            "view_audit": "audit:read"
        }
        
        permission = action_permission_map.get(action)
        if not permission:
            return True  # 未映射的动作默认允许
        
        return self.check_permission(user_id, permission)
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "department": user.department,
            "permissions": user.permissions
        }
    
    def list_users(self, role: Optional[UserRole] = None) -> List[Dict]:
        """列出用户"""
        users = list(self.users.values())
        
        if role:
            users = [u for u in users if u.role == role]
        
        return [
            {
                "user_id": u.user_id,
                "username": u.username,
                "email": u.email,
                "role": u.role.value,
                "department": u.department,
                "is_active": u.is_active
            }
            for u in users
        ]


# 使用权限管理
perm_manager = PermissionManager()
print("权限管理初始化完成")
print("用户列表:", perm_manager.list_users())
