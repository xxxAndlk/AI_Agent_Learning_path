import os
import importlib
import importlib.util
from pathlib import Path

class PluginRegistry:
    """插件注册中心"""
    
    def __init__(self, plugin_dir: str = "./plugins"):
        self.plugin_dir = plugin_dir
        self.plugin_classes: Dict[str, type] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        self.enabled_plugins: set = set()
    
    def scan_plugins(self) -> List[str]:
        """
        扫描目录发现插件
        
        返回:
            发现的插件列表
        """
        discovered = []
        
        if not os.path.exists(self.plugin_dir):
            return discovered
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]
                discovered.append(plugin_name)
        
        return discovered
    
    def load_plugin_module(self, plugin_name: str):
        """
        加载插件模块
        
        参数:
            plugin_name: 插件名称
        """
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        
        if not os.path.exists(plugin_path):
            raise FileNotFoundError(f"插件文件不存在: {plugin_path}")
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(
            plugin_name,
            plugin_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
    
    def register_plugin(
        self,
        plugin_class: type,
        config: Dict = None
    ):
        """
        注册插件类
        
        参数:
            plugin_class: 插件类
            config: 配置
        """
        # 获取类名作为插件名
        plugin_name = plugin_class.__name__
        
        self.plugin_classes[plugin_name] = plugin_class
        self.plugin_configs[plugin_name] = config or {}
    
    def get_plugin_class(self, plugin_name: str) -> Optional[type]:
        """获取插件类"""
        return self.plugin_classes.get(plugin_name)
    
    def enable_plugin(self, plugin_name: str):
        """启用插件"""
        self.enabled_plugins.add(plugin_name)
    
    def disable_plugin(self, plugin_name: str):
        """禁用插件"""
        self.enabled_plugins.discard(plugin_name)
    
    def list_plugins(self) -> List[Dict]:
        """列出所有插件"""
        return [
            {
                "name": name,
                "enabled": name in self.enabled_plugins,
                "has_config": name in self.plugin_configs
            }
            for name in self.plugin_classes.keys()
        ]


class AnnotationBasedRegistry:
    """基于注解的插件注册"""
    
    _plugins: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str = None):
        """装饰器注册插件"""
        def decorator(plugin_class):
            plugin_name = name or plugin_class.__name__
            cls._plugins[plugin_name] = plugin_class
            return plugin_class
        return decorator
    
    @classmethod
    def get_plugin(cls, name: str) -> Optional[type]:
        """获取插件类"""
        return cls._plugins.get(name)
    
    @classmethod
    def list_plugins(cls) -> List[str]:
        """列出所有注册的插件"""
        return list(cls._plugins.keys())


# 使用示例
@AnnotationBasedRegistry.register("my_plugin")
class MyPlugin(BasePlugin):
    """使用注解注册的插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="my_plugin",
            version="1.0.0",
            description="我的插件",
            author="User",
            dependencies=[],
            entry_point="MyPlugin",
            config={}
        )
    
    def initialize(self) -> bool:
        return True
    
    def execute(self, **kwargs) -> Any:
        return {"result": "success"}
