# 导入必要的标准库
from enum import Enum, auto                    # 枚举类型，用于定义权限级别
from typing import Dict, List, Set, Optional, Any  # 类型提示
from dataclasses import dataclass              # 数据类装饰器
import hashlib                                  # 哈希函数，用于日志处理
import json                                     # JSON处理

# 定义权限级别枚举
# 权限级别按数值递增，NONE为最低权限，ADMIN为最高权限
class PermissionLevel(Enum):
    """权限级别
    
    枚举定义四个权限等级：
    - NONE: 无任何权限
    - READ: 只读权限
    - WRITE: 可读写权限
    - EXECUTE: 可执行权限（包括读写）
    - ADMIN: 管理员权限
    """
    NONE = 0        # 无权限：不能进行任何操作
    READ = 1        # 只读：可以查看但不能修改
    WRITE = 2       # 可写：可以读取和修改
    EXECUTE = 3     # 可执行：可以执行操作
    ADMIN = 4       # 管理员：拥有所有权限


# 使用dataclass定义工具权限数据结构
# @dataclass自动生成__init__、__repr__等方法
@dataclass
class ToolPermission:
    """工具权限定义
    
    存储单个工具的所有权限配置信息
    """
    tool_name: str                    # 工具名称
    allowed_operations: Set[str]      # 允许的操作集合，如{"read", "write"}
    forbidden_params: Set[str]        # 禁止使用的参数集合
    max_calls_per_minute: int         # 每分钟最大调用次数限制
    require_approval: bool            # 是否需要管理员审批
    data_scope: Optional[str]         # 数据访问范围，None表示无限制


class PermissionManager:
    """权限管理器类
    
    核心权限管理组件，负责：
    - 定义和管理角色权限
    - 为用户分配角色
    - 验证工具调用权限
    - 实施调用频率限制
    """
    
    def __init__(self):
        """初始化权限管理器
        
        创建两个核心数据结构：
        - user_permissions: 存储每个用户的权限映射
        - role_permissions: 存储每个角色的权限定义
        - call_history: 记录用户调用历史用于频率限制
        """
        # 用户权限字典：user_id -> {tool_name -> ToolPermission}
        self.user_permissions: Dict[str, Dict[str, ToolPermission]] = {}
        
        # 角色权限字典：role_name -> {tool_name -> ToolPermission}
        self.role_permissions: Dict[str, Dict[str, ToolPermission]] = {}
        
        # 调用历史记录：key -> [timestamp列表]
        # 用于实现每分钟调用频率限制
        self.call_history: Dict[str, List[float]] = {}
    
    def define_role(self, role_name: str, permissions: Dict[str, ToolPermission]):
        """定义角色权限
        
        创建一个新角色并为其分配权限
        参数:
            role_name: 角色名称（如"developer"、"admin"）
            permissions: 该角色拥有的工具权限字典
        """
        # 将角色权限存储到角色权限字典中
        self.role_permissions[role_name] = permissions
    
    def assign_role(self, user_id: str, role_name: str):
        """为用户分配角色
        
        将用户的权限设置为对应角色的权限副本
        参数:
            user_id: 用户标识符
            role_name: 要分配的角色名称
        """
        # 检查角色是否存在
        if role_name in self.role_permissions:
            # 使用copy()创建副本，避免修改影响原始角色定义
            self.user_permissions[user_id] = self.role_permissions[role_name].copy()
    
    def check_tool_permission(
        self, 
        user_id: str,          # 用户ID
        tool_name: str,        # 工具名称
        operation: str,        # 要执行的操作
        params: Dict[str, Any] # 操作参数
    ) -> Dict[str, Any]:
        """检查工具调用权限
        
        核心权限验证方法，执行多层检查
        参数:
            user_id: 发起调用的用户ID
            tool_name: 要调用的工具名称
            operation: 要执行的操作类型
            params: 操作参数
        返回:
            权限检查结果字典
        """
        # 初始化检查结果
        result = {
            "allowed": False,           # 默认拒绝
            "reason": "",               # 拒绝原因
            "needs_approval": False,    # 是否需要审批
            "warnings": []              # 警告信息列表
        }
        
        # ===== 步骤1：获取用户权限 =====
        # 从用户权限字典中获取该用户的权限配置
        user_perms = self.user_permissions.get(user_id, {})
        
        # 获取该工具的具体权限配置
        tool_perm = user_perms.get(tool_name)
        
        # ===== 步骤2：检查工具访问权限 =====
        # 如果用户没有该工具的任何权限配置
        if not tool_perm:
            result["reason"] = f"用户无权限访问工具: {tool_name}"
            return result  # 直接返回拒绝
        
        # ===== 步骤3：检查操作权限 =====
        # 验证要执行的操作是否在允许列表中
        if operation not in tool_perm.allowed_operations:
            result["reason"] = f"操作 '{operation}' 不在允许列表中"
            return result
        
        # ===== 步骤4：检查禁止参数 =====
        # 验证参数中是否包含被禁止的参数
        for param in tool_perm.forbidden_params:
            if param in params:
                result["reason"] = f"参数 '{param}' 被禁止"
                return result
        
        # ===== 步骤5：检查调用频率限制 =====
        # 验证用户的调用频率是否超出限制
        if not self._check_rate_limit(user_id, tool_name, tool_perm.max_calls_per_minute):
            result["reason"] = "调用频率超限"
            return result
        
        # ===== 步骤6：检查审批要求 =====
        # 如果操作需要审批，设置标记
        if tool_perm.require_approval:
            result["needs_approval"] = True
            result["warnings"].append("此操作需要管理员审批")
        
        # 所有检查通过，允许执行
        result["allowed"] = True
        return result
    
    def _check_rate_limit(self, user_id: str, tool_name: str, max_calls: int) -> bool:
        """检查调用频率限制
        
        私有方法，实现每分钟调用次数限制
        参数:
            user_id: 用户ID
            tool_name: 工具名称
            max_calls: 允许的最大调用次数
        返回:
            是否允许调用
        """
        import time  # 导入时间模块
        
        # 构建缓存key：用户ID:工具名称
        key = f"{user_id}:{tool_name}"
        
        # 获取当前时间戳
        now = time.time()
        
        # 如果没有该key的记录，初始化为空列表
        if key not in self.call_history:
            self.call_history[key] = []
        
        # ===== 清理过期记录 =====
        # 移除60秒（1分钟）之前的调用记录
        # 列表推导式保留最近的调用记录
        self.call_history[key] = [
            t for t in self.call_history[key] 
            if now - t < 60  # 只保留60秒内的记录
        ]
        
        # ===== 检查频率限制 =====
        # 如果当前1分钟内的调用次数已达到限制
        if len(self.call_history[key]) >= max_calls:
            return False  # 拒绝调用
        
        # ===== 记录本次调用 =====
        # 将当前时间戳添加到调用历史
        self.call_history[key].append(now)
        
        return True  # 允许调用


class ToolSandbox:
    """工具沙箱环境类
    
    提供隔离的执行环境，用于：
    - 限制可执行的工具范围
    - 防止访问受限的文件路径
    - 记录所有执行操作
    """
    
    def __init__(self, allowed_tools: List[str], restricted_paths: List[str]):
        """初始化沙箱环境
        
        参数:
            allowed_tools: 允许执行的工具白名单
            restricted_paths: 禁止访问的路径列表
        """
        # 将工具列表转换为集合，提高查找效率
        self.allowed_tools = set(allowed_tools)
        
        # 将受限路径列表转换为集合
        self.restricted_paths = set(restricted_paths)
        
        # 初始化执行日志列表
        self.execution_log: List[Dict] = []
    
    def execute_tool(
        self, 
        tool_name: str,           # 工具名称
        params: Dict[str, Any],   # 工具参数
        user_id: str              # 用户ID
    ) -> Any:
        """在沙箱中执行工具
        
        核心执行方法，执行多层安全检查
        参数:
            tool_name: 要执行的工具名称
            params: 工具参数字典
            user_id: 发起调用的用户ID
        返回:
            执行结果
        异常:
            PermissionError: 当工具不在白名单或参数包含受限路径时
        """
        # ===== 步骤1：工具白名单检查 =====
        # 验证要执行的工具是否在允许列表中
        if tool_name not in self.allowed_tools:
            raise PermissionError(f"工具 {tool_name} 不在允许列表中")
        
        # ===== 步骤2：路径安全检查 =====
        # 检查参数中是否包含受保护的路径
        for key, value in params.items():
            # 只检查字符串类型的参数值
            if isinstance(value, str):
                # 遍历所有受限路径
                for restricted in self.restricted_paths:
                    # 如果参数值包含受限路径
                    if restricted in value:
                        raise PermissionError(f"参数包含受限路径: {restricted}")
        
        # ===== 步骤3：记录执行日志 =====
        # 创建日志条目，包含工具、参数、用户和时间戳
        # 使用MD5哈希截断作为时间戳标识
        self.execution_log.append({
            "tool": tool_name,
            "params": params,
            "user_id": user_id,
            "timestamp": hashlib.md5(str(params).encode()).hexdigest()[:8]
        })
        
        # ===== 步骤4：执行工具 =====
        # 此处为示例实现，实际应调用注册的工具
        return f"工具 {tool_name} 执行成功"


# ============ 使用示例函数 ============

def tool_permission_example():
    """工具权限控制示例
    
    演示PermissionManager和ToolSandbox的使用方法
    """
    
    # ===== 示例1：创建权限管理器 =====
    # 实例化权限管理器
    pm = PermissionManager()
    
    # ===== 示例2：定义角色权限 =====
    
    # 定义"developer"（开发者）角色权限
    pm.define_role("developer", {
        # 文件读取工具权限
        "file_reader": ToolPermission(
            tool_name="file_reader",
            allowed_operations={"read"},          # 只允许读取
            forbidden_params={"delete", "write"}, # 禁止删除和写入
            max_calls_per_minute=100,             # 每分钟100次限制
            require_approval=False,               # 不需要审批
            data_scope="/home/user/projects"      # 数据范围限制
        ),
        # 代码执行工具权限
        "code_executor": ToolPermission(
            tool_name="code_executor",
            allowed_operations={"execute"},       # 允许执行
            forbidden_params={"system_call", "network"},  # 禁止系统调用和网络
            max_calls_per_minute=20,              # 限制较严格
            require_approval=True,                # 需要审批
            data_scope=None                       # 无数据范围限制
        )
    })
    
    # 定义"admin"（管理员）角色权限
    pm.define_role("admin", {
        "file_reader": ToolPermission(
            tool_name="file_reader",
            allowed_operations={"read", "write", "delete"},  # 全部操作
            forbidden_params=set(),              # 无禁止参数
            max_calls_per_minute=1000,           # 高调用限制
            require_approval=False,              # 不需要审批
            data_scope="*"                       # 访问全部数据
        )
    })
    
    # ===== 示例3：分配角色给用户 =====
    pm.assign_role("user_001", "developer")
    pm.assign_role("admin_001", "admin")
    
    # ===== 示例4：测试权限验证 =====
    print("="*50)
    print("工具权限控制测试")
    print("="*50)
    
    # 测试1：Developer用户尝试读取文件 - 应该成功
    result = pm.check_tool_permission(
        "user_001", 
        "file_reader", 
        "read", 
        {"path": "/home/user/projects/code.py"}
    )
    print(f"Developer读文件: {'✓ 允许' if result['allowed'] else '✗ 拒绝'} - {result['reason']}")
    
    # 测试2：Developer用户尝试写入文件 - 应该失败
    result = pm.check_tool_permission(
        "user_001", 
        "file_reader", 
        "write", 
        {"path": "/home/user/projects/code.py"}
    )
    print(f"Developer写文件: {'✓ 允许' if result['allowed'] else '✗ 拒绝'} - {result['reason']}")
    
    # 测试3：Admin用户尝试删除文件 - 应该成功
    result = pm.check_tool_permission(
        "admin_001", 
        "file_reader", 
        "delete", 
        {"path": "/any/path"}
    )
    print(f"Admin删除文件: {'✓ 允许' if result['allowed'] else '✗ 拒绝'} - {result['reason']}")
    
    # ===== 示例5：沙箱环境测试 =====
    # 创建沙箱实例，只允许特定工具
    sandbox = ToolSandbox(
        allowed_tools=["calculator", "text_processor"],  # 白名单工具
        restricted_paths=["/etc", "/root", ".."]          # 受限路径
    )
    
    # 尝试执行允许的工具
    try:
        result = sandbox.execute_tool("calculator", {"expression": "1+1"}, "user_001")
        print(f"沙箱执行: {result}")
    except PermissionError as e:
        print(f"沙箱拒绝: {e}")


# ===== 程序入口 =====
if __name__ == "__main__":
    # 运行示例
    tool_permission_example()
