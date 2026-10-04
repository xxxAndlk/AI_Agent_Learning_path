import hashlib
import json
import time
from typing import Optional

class DynamicLoader:
    """动态加载器"""
    
    def __init__(self):
        self.loaded_modules: Dict[str, Any] = {}
        self.module_hashes: Dict[str, str] = {}
        self.watchers: List[callable] = []
    
    def load_module(
        self,
        module_path: str,
        module_name: str = None
    ) -> Any:
        """
        动态加载模块
        
        参数:
            module_path: 模块路径
            module_name: 模块名称
        
        返回:
            加载的模块
        """
        # 计算文件哈希
        file_hash = self._compute_hash(module_path)
        
        # 检查是否需要重新加载
        if module_name in self.loaded_modules:
            if self.module_hashes.get(module_name) == file_hash:
                return self.loaded_modules[module_name]
        
        # 动态加载
        spec = importlib.util.spec_from_file_location(
            module_name or "dynamic_module",
            module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 缓存
        self.loaded_modules[module_name] = module
        self.module_hashes[module_name] = file_hash
        
        return module
    
    def unload_module(self, module_name: str):
        """卸载模块"""
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]
            del self.module_hashes[module_name]
    
    def reload_module(self, module_path: str, module_name: str) -> Any:
        """
        热重载模块
        
        参数:
            module_path: 模块路径
            module_name: 模块名称
        
        返回:
            重新加载的模块
        """
        # 卸载旧模块
        self.unload_module(module_name)
        
        # 加载新模块
        return self.load_module(module_path, module_name)
    
    def _compute_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        hasher = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def watch_file(self, file_path: str, callback: callable):
        """监控文件变化"""
        self.watchers.append({
            'path': file_path,
            'callback': callback,
            'last_hash': self._compute_hash(file_path)
        })
    
    def check_updates(self):
        """检查文件更新"""
        for watcher in self.watchers:
            current_hash = self._compute_hash(watcher['path'])
            
            if current_hash != watcher['last_hash']:
                watcher['last_hash'] = current_hash
                watcher['callback'](watcher['path'])


class HotReloadManager:
    """热重载管理器"""
    
    def __init__(self):
        self.loader = DynamicLoader()
        self.plugin_instances: Dict[str, PluginInterface] = {}
    
    def load_with_reload(
        self,
        plugin_path: str,
        plugin_name: str,
        config: Dict = None
    ) -> Optional[PluginInterface]:
        """
        带热重载的加载
        
        参数:
            plugin_path: 插件路径
            plugin_name: 插件名称
            config: 配置
        
        返回:
            插件实例
        """
        try:
            # 加载模块
            module = self.loader.load_module(plugin_path, plugin_name)
            
            # 获取插件类
            plugin_class = getattr(module, plugin_name)
            
            # 创建实例
            plugin = plugin_class(config or {})
            
            # 初始化
            context = PluginContext(
                plugin_id=plugin_name,
                config=config or {},
                services={}
            )
            
            if plugin.initialize(context):
                self.plugin_instances[plugin_name] = plugin
                
                # 设置文件监控
                self.loader.watch_file(
                    plugin_path,
                    lambda p: self._handle_file_change(p, plugin_name)
                )
                
                return plugin
            
        except Exception as e:
            print(f"加载插件失败: {e}")
        
        return None
    
    def _handle_file_change(self, path: str, plugin_name: str):
        """处理文件变化"""
        print(f"检测到文件变化: {path}")
        
        # 停止旧实例
        if plugin_name in self.plugin_instances:
            old_plugin = self.plugin_instances[plugin_name]
            old_plugin.stop()
        
        # 重新加载
        self.loader.reload_module(path, plugin_name)
