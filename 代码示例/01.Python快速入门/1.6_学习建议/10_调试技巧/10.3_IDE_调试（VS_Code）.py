# VS Code 调试配置示例
# 创建 .vscode/launch.json

"""
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: 当前文件",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: 远程调试",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            }
        }
    ]
}
"""

# VS Code 调试技巧：
# 1. F5 开始调试
# 2. F9 设置/取消断点
# 3. F10 单步跳过
# 4. F11 单步进入
# 5. Shift+F11 单步退出
# 6. 变量窗口查看所有局部变量
# 7. 监视窗口添加自定义表达式

# 条件断点示例
# 在断点处右键 -> 编辑条件
# 输入条件表达式，如 i > 10
