from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class PluginState(Enum):
    """插件生命周期状态"""
    REGISTERED = "registered"      # 已注册
    LOADING = "loading"            # 加载中
    READY = "ready"                # 就绪
    RUNNING = "running"            # 运行中
    STOPPED = "stopped"            # 已停止
    ERROR = "error"                # 错误
    UNLOADED = "unloaded"          # 已卸载


@dataclass
class PluginMetadata:
    """插件元数据"""
    id: str                        # 唯一标识
    name: str                      # 插件名称
    version: str                   # 版本号
    description: str               # 描述
    author: str                    # 作者
    entry_point: str               # 入口类
    dependencies: List[str] = field(default_factory=list)  # 依赖
    permissions: List[str] = field(default_factory=list)   # 权限
    config_schema: Dict[str, Any] = field(default_factory=dict)  # 配置模式
    tags: List[str] = field(default_factory=list)          # 标签


@dataclass
class PluginContext:
    """插件执行上下文"""
    plugin_id: str
    config: Dict[str, Any]
    services: Dict[str, Any]  # 可用的服务


class PluginInterface(ABC):
    """插件接口定义"""
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """获取插件元数据"""
        pass
    
    @abstractmethod
    def initialize(self, context: PluginContext) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """启动插件"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """停止插件"""
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """执行插件功能"""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        pass


class PluginArchitecture:
    """插件架构设计器"""
    
    def __init__(self):
        self.interfaces: Dict[str, Type[PluginInterface]] = {}
        self.implementations: Dict[str, PluginInterface] = {}
        self.contexts: Dict[str, PluginContext] = {}
    
    def register_interface(
        self,
        interface_name: str,
        interface_class: Type[PluginInterface]
    ):
        """注册插件接口"""
        self.interfaces[interface_name] = interface_class
    
    def create_plugin(
        self,
        metadata: PluginMetadata,
        implementation: PluginInterface
    ) -> bool:
        """
        创建插件实例
        
        参数:
            metadata: 插件元数据
            implementation: 插件实现
        
        返回:
            是否成功
        """
        # 验证接口
        interface_name = metadata.entry_point
        if interface_name not in self.interfaces:
            return False
        
        # 检查依赖
        for dep in metadata.dependencies:
            if dep not in self.implementations:
                return False
        
        # 创建上下文
        context = PluginContext(
            plugin_id=metadata.id,
            config={},
            services={}
        )
        
        # 初始化插件
        if not implementation.initialize(context):
            return False
        
        # 注册实现
        self.implementations[metadata.id] = implementation
        self.contexts[metadata.id] = context
        
        return True
