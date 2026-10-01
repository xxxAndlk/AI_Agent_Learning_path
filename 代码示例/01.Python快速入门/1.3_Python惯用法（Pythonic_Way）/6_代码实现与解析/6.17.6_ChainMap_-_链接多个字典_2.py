# 实际案例：命令行参数与默认配置合并
from collections import ChainMap

# 默认配置
default_config = {
    'host': 'localhost',
    'port': 8080,
    'debug': False,
    'log_level': 'INFO',
}

# 用户配置文件
user_config = {
    'port': 9000,
    'debug': True,
}

# 环境变量
env_config = {
    'log_level': 'DEBUG',
}

# 优先级：环境变量 > 用户配置 > 默认配置
config = ChainMap(env_config, user_config, default_config)

print(f"Host: {config['host']}")      # localhost（来自默认）
print(f"Port: {config['port']}")      # 9000（来自用户配置）
print(f"Debug: {config['debug']}")    # True（来自用户配置）
print(f"Log: {config['log_level']}")  # DEBUG（来自环境变量）

# 实际案例：变量作用域模拟
global_vars = {'name': 'global', 'version': '1.0'}
module_vars = {'name': 'module', 'author': 'Alice'}
function_vars = {'name': 'function'}

# 模拟函数作用域查找
scope = ChainMap(function_vars, module_vars, global_vars)
print(f"Name: {scope['name']}")      # function（局部优先）
print(f"Version: {scope['version']}") # 1.0（全局）
