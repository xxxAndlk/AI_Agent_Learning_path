class PluginLifecycleManager:
    """插件生命周期管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.states: Dict[str, PluginState] = {}
        self.listeners: List[callable] = []
    
    async def load_plugin(
        self,
        plugin: PluginInterface,
        config: Dict[str, Any]
    ) -> bool:
        """
        加载插件
        
        参数:
            plugin: 插件实例
            config: 配置
        
        返回:
            是否成功
        """
        metadata = plugin.get_metadata()
        plugin_id = metadata.id
        
        # 检查是否已加载
        if plugin_id in self.plugins:
            return False
        
        # 检查依赖
        if not self._check_dependencies(metadata):
            return False
        
        # 创建上下文
        context = PluginContext(
            plugin_id=plugin_id,
            config=config,
            services=self._get_services()
        )
        
        # 初始化
        self.states[plugin_id] = PluginState.LOADING
        self._notify_listeners("before_load", plugin_id)
        
        if not plugin.initialize(context):
            self.states[plugin_id] = PluginState.ERROR
            return False
        
        # 注册插件
        self.plugins[plugin_id] = plugin
        self.states[plugin_id] = PluginState.READY
        
        self._notify_listeners("after_load", plugin_id)
        
        return True
    
    async def start_plugin(self, plugin_id: str) -> bool:
        """启动插件"""
        if plugin_id not in self.plugins:
            return False
        
        if self.states[plugin_id] != PluginState.READY:
            return False
        
        self.states[plugin_id] = PluginState.RUNNING
        self._notify_listeners("before_start", plugin_id)
        
        plugin = self.plugins[plugin_id]
        success = plugin.start()
        
        if success:
            self._notify_listeners("after_start", plugin_id)
        else:
            self.states[plugin_id] = PluginState.ERROR
        
        return success
    
    async def stop_plugin(self, plugin_id: str) -> bool:
        """停止插件"""
        if plugin_id not in self.plugins:
            return False
        
        self._notify_listeners("before_stop", plugin_id)
        
        plugin = self.plugins[plugin_id]
        success = plugin.stop()
        
        if success:
            self.states[plugin_id] = PluginState.STOPPED
            self._notify_listeners("after_stop", plugin_id)
        
        return success
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id not in self.plugins:
            return False
        
        # 先停止
        if self.states[plugin_id] == PluginState.RUNNING:
            await self.stop_plugin(plugin_id)
        
        # 检查依赖
        if self._has_dependents(plugin_id):
            return False
        
        # 卸载
        del self.plugins[plugin_id]
        self.states[plugin_id] = PluginState.UNLOADED
        
        self._notify_listeners("after_unload", plugin_id)
        
        return True
    
    def _check_dependencies(self, metadata: PluginMetadata) -> bool:
        """检查依赖"""
        for dep in metadata.dependencies:
            if dep not in self.plugins:
                return False
            if self.states.get(dep) not in [PluginState.READY, PluginState.RUNNING]:
                return False
        return True
    
    def _has_dependents(self, plugin_id: str) -> bool:
        """检查是否有依赖此插件的其他插件"""
        for metadata in [p.get_metadata() for p in self.plugins.values()]:
            if plugin_id in metadata.dependencies:
                return True
        return False
    
    def _get_services(self) -> Dict[str, Any]:
        """获取可用的服务"""
        return {}
    
    def _notify_listeners(self, event: str, plugin_id: str):
        """通知监听器"""
        for listener in self.listeners:
            try:
                listener(event, plugin_id)
            except:
                pass
    
    def add_listener(self, listener: callable):
        """添加事件监听器"""
        self.listeners.append(listener)
