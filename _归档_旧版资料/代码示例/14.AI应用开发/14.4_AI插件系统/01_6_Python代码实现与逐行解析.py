from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import os
import json


class PluginStatus(Enum):
    """插件状态"""
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"

@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    entry_point: str
    config: Dict[str, Any]

class BasePlugin(ABC):
    """插件基类 - 定义插件的标准接口"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.status = PluginStatus.LOADED
        self.info = self.get_info()
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行插件功能"""
        pass
    
    def shutdown(self):
        """关闭插件"""
        self.status = PluginStatus.DISABLED
    
    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return []


# 示例插件：计算器插件
class CalculatorPlugin(BasePlugin):
    """计算器插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="calculator",
            version="1.0.0",
            description="支持基本数学运算",
            author="System",
            dependencies=[],
            entry_point="CalculatorPlugin",
            config={}
        )
    
    def initialize(self) -> bool:
        print(f"[插件] {self.info.name} 初始化成功")
        self.status = PluginStatus.ENABLED
        return True
    
    def execute(self, expression: str, **kwargs) -> Dict[str, Any]:
        """执行计算"""
        try:
            # 安全计算（使用eval需限制）
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return {"success": False, "error": "表达式包含非法字符"}
            
            result = eval(expression)
            return {
                "success": True,
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        return ["calculator", "math"]


# 示例插件：搜索插件
class SearchPlugin(BasePlugin):
    """搜索插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="web_search",
            version="1.0.0",
            description="网络搜索功能",
            author="System",
            dependencies=["requests"],
            entry_point="SearchPlugin",
            config={"api_key": ""}
        )
    
    def initialize(self) -> bool:
        self.status = PluginStatus.ENABLED
        return True
    
    def execute(self, query: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """执行搜索"""
        # 模拟搜索
        results = [
            {"title": f"搜索结果 {i}", "url": f"https://example.com/{i}", "snippet": f"关于 {query} 的内容..."}
            for i in range(top_k)
        ]
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total": len(results)
        }
    
    def get_capabilities(self) -> List[str]:
        return ["search", "web_search"]


# 插件管理器
class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, type] = {}
    
    def register_plugin_class(self, name: str, plugin_class: type):
        """注册插件类"""
        self.plugin_classes[name] = plugin_class
    
    def instantiate_plugin(self, plugin_name: str, config: Dict = None) -> Optional[BasePlugin]:
        """实例化插件"""
        if plugin_name not in self.plugin_classes:
            return None
        
        plugin_class = self.plugin_classes[plugin_name]
        plugin = plugin_class(config)
        
        # 初始化
        if plugin.initialize():
            self.plugins[plugin_name] = plugin
            return plugin
        
        return None
    
    def execute_plugin(self, name: str, **kwargs) -> Any:
        """执行插件"""
        plugin = self.get_plugin(name)
        if not plugin:
            return {"error": f"插件 {name} 未找到"}
        
        if plugin.status != PluginStatus.ENABLED:
            return {"error": f"插件 {name} 未启用"}
        
        try:
            return plugin.execute(**kwargs)
        except Exception as e:
            return {"error": str(e)}
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict]:
        """列出所有插件"""
        return [
            {
                "name": name,
                "version": plugin.info.version,
                "status": plugin.status.value,
                "capabilities": plugin.get_capabilities()
            }
            for name, plugin in self.plugins.items()
        ]


def main():
    """主函数"""
    # 创建插件管理器
    manager = PluginManager()
    
    # 注册插件
    manager.register_plugin_class("calculator", CalculatorPlugin)
    manager.register_plugin_class("web_search", SearchPlugin)
    
    # 实例化插件
    calc_plugin = manager.instantiate_plugin("calculator")
    search_plugin = manager.instantiate_plugin("web_search")
    
    # 列出插件
    print("\n已加载插件:")
    for info in manager.list_plugins():
        print(f"  - {info['name']} v{info['version']} [{info['status']}]")
        print(f"    能力: {', '.join(info['capabilities'])}")
    
    # 执行插件
    print("\n" + "="*60)
    print("执行插件")
    print("="*60)
    
    # 计算器
    result = manager.execute_plugin("calculator", expression="(100 + 200) * 3")
    print(f"\n计算结果: {result}")
    
    # 搜索
    result = manager.execute_plugin("web_search", query="Python插件系统", top_k=3)
    print(f"\n搜索结果: {result['total']} 条")


if __name__ == "__main__":
    main()
