"""
完整的企业级AI插件系统

包含：
- 插件接口定义
- 插件生命周期管理
- 动态加载
- 版本管理
- 安全隔离
- 完整示例
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnterprisePluginSystem:
    """企业级AI插件系统"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化系统
        
        参数:
            config: 系统配置
        """
        self.config = config or {}
        
        # 初始化各个组件
        self.registry = PluginRegistry(
            self.config.get('plugin_dir', './plugins')
        )
        self.lifecycle_manager = PluginLifecycleManager()
        self.version_manager = PluginVersionManager()
        self.loader = DynamicLoader()
        
        # 插件实例
        self.plugins: Dict[str, PluginInterface] = {}
        
        # 启用禁用列表
        self.disabled_plugins: set = set()
    
    def initialize(self) -> bool:
        """初始化系统"""
        logger.info("初始化插件系统...")
        
        # 扫描并加载插件
        discovered = self.registry.scan_plugins()
        logger.info(f"发现 {len(discovered)} 个插件: {discovered}")
        
        return True
    
    def load_plugin(
        self,
        plugin_name: str,
        config: Dict = None,
        enable: bool = True
    ) -> bool:
        """
        加载插件
        
        参数:
            plugin_name: 插件名称
            config: 插件配置
            enable: 是否立即启用
        
        返回:
            是否成功
        """
        try:
            # 获取插件类
            plugin_class = self.registry.get_plugin_class(plugin_name)
            
            if not plugin_class:
                logger.error(f"插件类未找到: {plugin_name}")
                return False
            
            # 创建实例
            plugin = plugin_class(config or {})
            
            # 加载插件
            success = asyncio.run(
                self.lifecycle_manager.load_plugin(plugin, config or {})
            )
            
            if success:
                self.plugins[plugin_name] = plugin
                self.version_manager.register_version(
                    plugin_name,
                    plugin.get_info().version
                )
                
                if enable:
                    self.enable_plugin(plugin_name)
                
                logger.info(f"插件加载成功: {plugin_name}")
                return True
            
            logger.error(f"插件加载失败: {plugin_name}")
            return False
        
        except Exception as e:
            logger.error(f"加载插件异常: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        if plugin_name not in self.plugins:
            return False
        
        self.disabled_plugins.discard(plugin_name)
        
        success = asyncio.run(
            self.lifecycle_manager.start_plugin(plugin_name)
        )
        
        if success:
            logger.info(f"插件已启用: {plugin_name}")
        
        return success
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        success = asyncio.run(
            self.lifecycle_manager.stop_plugin(plugin_name)
        )
        
        if success:
            self.disabled_plugins.add(plugin_name)
            logger.info(f"插件已禁用: {plugin_name}")
        
        return success
    
    def execute_plugin(
        self,
        plugin_name: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        执行插件
        
        参数:
            plugin_name: 插件名称
            params: 参数
        
        返回:
            执行结果
        """
        if plugin_name in self.disabled_plugins:
            return {"error": "插件已禁用"}
        
        if plugin_name not in self.plugins:
            return {"error": "插件不存在"}
        
        plugin = self.plugins[plugin_name]
        
        try:
            result = plugin.execute(params)
            return result
        
        except Exception as e:
            logger.error(f"执行插件异常: {e}")
            return {"error": str(e)}
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        if plugin_name not in self.plugins:
            return False
        
        # 禁用
        if plugin_name not in self.disabled_plugins:
            self.disable_plugin(plugin_name)
        
        # 卸载
        success = asyncio.run(
            self.lifecycle_manager.unload_plugin(plugin_name)
        )
        
        if success:
            del self.plugins[plugin_name]
            logger.info(f"插件已卸载: {plugin_name}")
        
        return success
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'total_plugins': len(self.plugins),
            'enabled_plugins': len(self.plugins) - len(self.disabled_plugins),
            'disabled_plugins': len(self.disabled_plugins),
            'plugins': [
                {
                    'name': name,
                    'version': p.get_info().version,
                    'enabled': name not in self.disabled_plugins,
                    'state': self.lifecycle_manager.states.get(name, 'unknown').value
                }
                for name, p in self.plugins.items()
            ]
        }


# 插件示例
class DataProcessPlugin(BasePlugin):
    """数据处理插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="data_processor",
            version="1.0.0",
            description="数据处理插件",
            author="Enterprise",
            dependencies=[],
            entry_point="DataProcessPlugin",
            config={}
        )
    
    def initialize(self, context: PluginContext) -> bool:
        logger.info("数据处理插件初始化")
        return True
    
    def start(self) -> bool:
        return True
    
    def stop(self) -> bool:
        return True
    
    def execute(self, params: Dict[str, Any]) -> Any:
        data = params.get('data', [])
        operation = params.get('operation', 'sum')
        
        if operation == 'sum':
            return {'result': sum(data)}
        elif operation == 'avg':
            return {'result': sum(data) / len(data) if data else 0}
        else:
            return {'error': f'未知操作: {operation}'}
    
    def get_health_status(self) -> Dict[str, Any]:
        return {'status': 'healthy'}


class AIParserPlugin(BasePlugin):
    """AI解析插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="ai_parser",
            version="1.2.0",
            description="AI文本解析插件",
            author="Enterprise",
            dependencies=["data_processor"],
            entry_point="AIParserPlugin",
            config={}
        )
    
    def initialize(self, context: PluginContext) -> bool:
        logger.info("AI解析插件初始化")
        return True
    
    def start(self) -> bool:
        return True
    
    def stop(self) -> bool:
        return True
    
    def execute(self, params: Dict[str, Any]) -> Any:
        text = params.get('text', '')
        
        # 简化解析
        return {
            'text': text,
            'word_count': len(text),
            'characters': len(text)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        return {'status': 'healthy'}


def main():
    """主函数"""
    # 创建系统
    system = EnterprisePluginSystem({
        'plugin_dir': './plugins'
    })
    
    # 初始化
    system.initialize()
    
    # 注册插件
    system.registry.register_plugin(DataProcessPlugin)
    system.registry.register_plugin(AIParserPlugin)
    
    # 加载插件
    system.load_plugin('data_processor', enable=True)
    system.load_plugin('ai_parser', enable=True)
    
    # 执行插件
    print("\n执行数据处理插件:")
    result = system.execute_plugin('data_processor', {
        'data': [1, 2, 3, 4, 5],
        'operation': 'sum'
    })
    print(f"结果: {result}")
    
    print("\n执行AI解析插件:")
    result = system.execute_plugin('ai_parser', {
        'text': '这是一段测试文本'
    })
    print(f"结果: {result}")
    
    # 系统状态
    print("\n系统状态:")
    status = system.get_system_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
