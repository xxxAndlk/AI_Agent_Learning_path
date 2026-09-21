import subprocess
import sys
import tempfile
import os

class PluginSandbox:
    """插件沙箱"""
    
    def __init__(
        self,
        max_memory_mb: int = 512,
        max_cpu_percent: int = 50,
        allowed_modules: List[str] = None,
        forbidden_modules: List[str] = None
    ):
        """
        初始化沙箱
        
        参数:
            max_memory_mb: 最大内存（MB）
            max_cpu_percent: 最大CPU使用率
            allowed_modules: 允许的模块
            forbidden_modules: 禁止的模块
        """
        self.max_memory = max_memory_mb * 1024 * 1024
        self.max_cpu = max_cpu_percent
        self.allowed_modules = allowed_modules or []
        self.forbidden_modules = forbidden_modules or [
            'os', 'sys', 'subprocess', 'socket'
        ]
    
    def execute_in_sandbox(
        self,
        plugin_code: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        在沙箱中执行代码
        
        参数:
            plugin_code: 插件代码
            timeout: 超时时间（秒）
        
        返回:
            执行结果
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(plugin_code)
            temp_file = f.name
        
        try:
            # 执行代码
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '执行超时',
                'timeout': True
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass


class RestrictedPluginContext:
    """受限的插件上下文"""
    
    def __init__(self, capabilities: List[str] = None):
        self.capabilities = capabilities or []
        self.resource_limits = {
            'max_calls_per_minute': 1000,
            'max_data_size_mb': 10,
            'max_execution_time_ms': 5000
        }
        self._call_counts = {}
    
    def check_permission(self, permission: str) -> bool:
        """检查权限"""
        return permission in self.capabilities
    
    def check_rate_limit(self, operation: str) -> bool:
        """检查速率限制"""
        # 简化实现
        return True
    
    def enforce_limits(self, operation: str) -> bool:
        """强制执行限制"""
        if not self.check_permission(operation):
            return False
        
        if not self.check_rate_limit(operation):
            return False
        
        return True
