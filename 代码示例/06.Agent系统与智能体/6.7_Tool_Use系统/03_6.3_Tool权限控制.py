"""
Tool权限控制系统
实现工具调用的安全控制机制
"""

# 导入所需模块
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass  # 数据类
from datetime import datetime  # 日期时间
import hashlib  # 哈希加密
import json  # JSON处理

@dataclass
class ToolPermission:
    """工具权限定义数据类"""
    tool_name: str                     # 工具名称： "*"表示所有工具
    allow_read: bool = True            # 是否允许读取操作
    allow_write: bool = False          # 是否允许写入操作（修改数据）
    allow_delete: bool = False         # 是否允许删除操作
    rate_limit: int = 100              # 每分钟调用次数限制
    allowed_params: Optional[Set[str]] = None   # 允许使用的参数白名单
    forbidden_params: Optional[Set[str]] = None # 禁止使用的参数黑名单


@dataclass
class UserRole:
    """用户角色数据类"""
    role_id: str                       # 角色ID：唯一标识
    role_name: str                     # 角色名称：显示名称
    permissions: List[ToolPermission]  # 权限列表：该角色拥有的权限


class PermissionManager:
    """权限管理器类 - 核心的权限控制组件"""
    
    def __init__(self):
        """初始化权限管理器"""
        self.roles: Dict[str, UserRole] = {}      # 角色定义字典
        self.user_roles: Dict[str, List[str]] = {}  # 用户-角色映射
        self.call_records: List[Dict] = []          # 调用记录（用于审计）
    
    def create_role(self, role_id: str, role_name: str) -> UserRole:
        """
        创建新角色
        
        参数:
            role_id: 角色唯一标识
            role_name: 角色显示名称
        返回:
            创建的UserRole对象
        """
        role = UserRole(role_id, role_name, [])
        self.roles[role_id] = role
        return role
    
    def add_permission_to_role(self, role_id: str, permission: ToolPermission):
        """
        为角色添加权限
        
        参数:
            role_id: 角色ID
            permission: 权限定义对象
        """
        if role_id in self.roles:
            self.roles[role_id].permissions.append(permission)
    
    def assign_role_to_user(self, user_id: str, role_id: str):
        """
        为用户分配角色（用户可以有多个角色）
        
        参数:
            user_id: 用户ID
            role_id: 角色ID
        """
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []  # 初始化用户的角色列表
        if role_id not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_id)
    
    def check_permission(self, user_id: str, tool_name: str, action: str = "read") -> bool:
        """
        检查用户是否有权限执行操作
        
        参数:
            user_id: 用户ID
            tool_name: 工具名称
            action: 操作类型（read/write/delete）
        返回:
            是否有权限（True/False）
        """
        # 获取用户的所有角色
        user_role_ids = self.user_roles.get(user_id, [])
        
        # 遍历用户的每个角色
        for role_id in user_role_ids:
            role = self.roles.get(role_id)
            if not role:
                continue
            
            # 遍历角色中的每个权限定义
            for perm in role.permissions:
                # 匹配工具名称（支持通配符"*"）
                if perm.tool_name == tool_name or perm.tool_name == "*":
                    # 根据操作类型检查对应权限
                    if action == "read" and perm.allow_read:
                        return True
                    if action == "write" and perm.allow_write:
                        return True
                    if action == "delete" and perm.allow_delete:
                        return True
        
        return False  # 所有角色都没有权限
    
    def validate_parameters(self, user_id: str, tool_name: str, params: Dict) -> tuple:
        """
        验证参数使用权限（白名单/黑名单）
        
        参数:
            user_id: 用户ID
            tool_name: 工具名称
            params: 调用参数字典
        返回:
            (is_valid, error_message) 元组
        """
        user_role_ids = self.user_roles.get(user_id, [])
        
        for role_id in user_role_ids:
            role = self.roles.get(role_id)
            if not role:
                continue
            
            # 查找该工具的权限定义
            for perm in role.permissions:
                if perm.tool_name == tool_name:
                    # 检查参数白名单（如果设置）
                    if perm.allowed_params:
                        for param in params:
                            if param not in perm.allowed_params:
                                return False, f"参数'{param}'不在允许列表中"
                    
                    # 检查参数黑名单（如果设置）
                    if perm.forbidden_params:
                        for param in params:
                            if param in perm.forbidden_params:
                                return False, f"参数'{param}'被禁止使用"
        
        return True, ""  # 参数验证通过


class SecureToolExecutor:
    """安全工具执行器类 - 在权限控制下执行工具"""
    
    def __init__(self, permission_manager: PermissionManager):
        """
        初始化安全执行器
        
        参数:
            permission_manager: 权限管理器实例
        """
        self.pm = permission_manager
        self.tool_handlers: Dict[str, callable] = {}  # 工具处理器映射
        self.call_history: Dict[str, List[datetime]] = {}  # 调用历史（用于限流）
    
    def register_tool_handler(self, tool_name: str, handler: callable):
        """
        注册工具处理器（实际执行逻辑）
        
        参数:
            tool_name: 工具名称
            handler: 处理函数（callable）
        """
        self.tool_handlers[tool_name] = handler
    
    def execute(self, user_id: str, tool_name: str, params: Dict, action: str = "read") -> Dict:
        """
        安全执行工具调用（核心执行方法）
        
        参数:
            user_id: 用户ID
            tool_name: 工具名称
            params: 调用参数
            action: 操作类型
        返回:
            包含success和result/error的字典
        """
        # 第一步：权限检查
        if not self.pm.check_permission(user_id, tool_name, action):
            return {
                "success": False,
                "error": f"权限不足：用户'{user_id}'没有'{action}'权限使用工具'{tool_name}'"
            }
        
        # 第二步：参数权限验证
        is_valid, error_msg = self.pm.validate_parameters(user_id, tool_name, params)
        if not is_valid:
            return {
                "success": False,
                "error": f"参数验证失败：{error_msg}"
            }
        
        # 第三步：限流检查
        if not self._check_rate_limit(user_id, tool_name):
            return {
                "success": False,
                "error": "调用频率超限，请稍后重试"
            }
        
        # 第四步：记录调用（用于审计）
        self._record_call(user_id, tool_name)
        
        # 第五步：执行工具实际逻辑
        try:
            handler = self.tool_handlers.get(tool_name)
            if not handler:
                return {
                    "success": False,
                    "error": f"工具'{tool_name}'未注册"
                }
            
            # 调用处理器函数
            result = handler(**params)
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"执行错误：{str(e)}"
            }
    
    def _check_rate_limit(self, user_id: str, tool_name: str) -> bool:
        """检查调用频率是否超限"""
        key = f"{user_id}:{tool_name}"  # 构建唯一键
        now = datetime.now()
        
        # 初始化调用历史
        if key not in self.call_history:
            self.call_history[key] = []
        
        # 清理1分钟前的历史记录（只保留最近1分钟）
        self.call_history[key] = [
            t for t in self.call_history[key]
            if (now - t).seconds < 60
        ]
        
        # 获取该工具的限流配置（默认100次/分钟）
        limit = 100
        user_role_ids = self.pm.user_roles.get(user_id, [])
        for role_id in user_role_ids:
            role = self.pm.roles.get(role_id)
            if role:
                for perm in role.permissions:
                    if perm.tool_name == tool_name:
                        limit = perm.rate_limit
                        break
        
        # 检查是否超过限制
        return len(self.call_history[key]) < limit
    
    def _record_call(self, user_id: str, tool_name: str):
        """记录工具调用"""
        key = f"{user_id}:{tool_name}"
        if key not in self.call_history:
            self.call_history[key] = []
        self.call_history[key].append(datetime.now())


# 使用示例
if __name__ == "__main__":
    # 创建权限管理器
    pm = PermissionManager()
    
    # 创建角色
    admin_role = pm.create_role("admin", "管理员")
    user_role = pm.create_role("user", "普通用户")
    
    # 配置管理员权限（所有工具，完全访问，高限流）
    pm.add_permission_to_role("admin", ToolPermission(
        tool_name="*",  # 通配符表示所有工具
        allow_read=True,
        allow_write=True,
        allow_delete=True,
        rate_limit=1000  # 管理员每分钟1000次
    ))
    
    # 配置普通用户权限（限制访问）
    pm.add_permission_to_role("user", ToolPermission(
        tool_name="calculator",
        allow_read=True,
        allow_write=False,
        rate_limit=50  # 每分钟50次
    ))
    pm.add_permission_to_role("user", ToolPermission(
        tool_name="weather",
        allow_read=True,
        rate_limit=30  # 每分钟30次
    ))
    
    # 分配角色给用户
    pm.assign_role_to_user("user001", "user")
    pm.assign_role_to_user("admin001", "admin")
    
    # 创建安全执行器
    executor = SecureToolExecutor(pm)
    
    # 注册工具处理器（实际执行函数）
    executor.register_tool_handler("calculator", lambda expression: eval(expression))
    executor.register_tool_handler("weather", lambda city: f"{city}天气：晴天 25°C")
    
    # 测试权限控制
    print("=== 权限控制测试 ===\n")
    
    # 普通用户测试
    print("普通用户(user001)测试:")
    result = executor.execute("user001", "calculator", {"expression": "15 + 25"})
    print(f"  计算器调用: {'成功' if result['success'] else '失败'}")
    
    # 测试删除权限（应该被拒绝）
    result = executor.execute("user001", "database", {"action": "delete"}, action="delete")
    print(f"  数据库删除: {'成功' if result['success'] else '失败'} - {result.get('error', '')}")
    
    # 管理员测试
    print("\n管理员(admin001)测试:")
    result = executor.execute("admin001", "calculator", {"expression": "100 / 4"})
    print(f"  计算器调用: {'成功' if result['success'] else '失败'}")
    print(f"  结果: {result.get('result')}")
