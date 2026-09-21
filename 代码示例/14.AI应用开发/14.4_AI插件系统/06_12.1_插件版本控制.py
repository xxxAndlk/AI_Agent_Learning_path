from packaging import version
import semver

class PluginVersionManager:
    """插件版本管理器"""
    
    def __init__(self):
        self.plugin_versions: Dict[str, str] = {}
        self.version_constraints: Dict[str, Dict[str, str]] = {}
    
    def register_version(
        self,
        plugin_name: str,
        plugin_version: str
    ):
        """
        注册插件版本
        
        参数:
            plugin_name: 插件名称
            plugin_version: 版本号
        """
        self.plugin_versions[plugin_name] = plugin_version
    
    def check_compatibility(
        self,
        plugin_name: str,
        required_version: str
    ) -> bool:
        """
        检查版本兼容性
        
        参数:
            plugin_name: 插件名称
            required_version: 要求的版本
        
        返回:
            是否兼容
        """
        if plugin_name not in self.plugin_versions:
            return False
        
        current = self.plugin_versions[plugin_name]
        
        try:
            # 使用语义版本比较
            return version.parse(current) >= version.parse(required_version)
        except:
            return False
    
    def upgrade_plugin(
        self,
        plugin_name: str,
        new_version: str,
        migration_fn: callable = None
    ) -> bool:
        """
        升级插件
        
        参数:
            plugin_name: 插件名称
            new_version: 新版本
            migration_fn: 迁移函数
        
        返回:
            是否成功
        """
        if plugin_name not in self.plugin_versions:
            return False
        
        old_version = self.plugin_versions[plugin_name]
        
        # 执行迁移
        if migration_fn:
            if not migration_fn(old_version, new_version):
                return False
        
        # 更新版本
        self.plugin_versions[plugin_name] = new_version
        
        return True
    
    def get_installed_version(self, plugin_name: str) -> Optional[str]:
        """获取已安装版本"""
        return self.plugin_versions.get(plugin_name)
    
    def list_outdated(self) -> List[Dict]:
        """列出需要更新的插件"""
        # 省略检查逻辑
        return []


class PluginDependencyResolver:
    """插件依赖解析器"""
    
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
    
    def add_dependency(
        self,
        plugin_name: str,
        depends_on: str,
        version_constraint: str = None
    ):
        """添加依赖关系"""
        if plugin_name not in self.dependencies:
            self.dependencies[plugin_name] = []
        
        self.dependencies[plugin_name].append(depends_on)
    
    def resolve_dependencies(
        self,
        plugin_name: str
    ) -> List[str]:
        """
        解析依赖（拓扑排序）
        
        参数:
            plugin_name: 插件名称
        
        返回:
            加载顺序
        """
        visited = set()
        stack = []
        
        def dfs(name: str):
            if name in visited:
                return
            visited.add(name)
            
            # 先加载依赖
            for dep in self.dependencies.get(name, []):
                dfs(dep)
            
            stack.append(name)
        
        dfs(plugin_name)
        
        return stack
    
    def detect_conflicts(
        self,
        plugins: List[Dict[str, str]]
    ) -> List[Dict]:
        """
        检测版本冲突
        
        参数:
            plugins: 插件列表（名称和版本）
        
        返回:
            冲突列表
        """
        conflicts = []
        
        # 简化版冲突检测
        for i, p1 in enumerate(plugins):
            for p2 in plugins[i+1:]:
                if p1['name'] == p2['name']:
                    if p1['version'] != p2['version']:
                        conflicts.append({
                            'plugin': p1['name'],
                            'versions': [p1['version'], p2['version']]
                        })
        
        return conflicts
