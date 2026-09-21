# 1. 改进的 subprocess 管理
import subprocess

# Python 3.12+ 支持 use_shell_form 语法检测
# 建议使用 list 形式而非字符串
subprocess.run(["ls", "-la"])  # 推荐
# 之前的 subprocess.run("ls -la") 会收到警告

# 2. 改进的 typing 模块
from typing import TypeAlias, Self

# TypeAlias 简化类型别名定义
type StringList = list[str]

# Self 类型（在类中使用）
class Node:
    def create_child(self) -> Self:  # 返回类型为当前类
        return Self()

# 3. 改进的 os.PathLike
from os import PathLike

class MyPath:
    def __fspath__(self) -> str:
        return "/my/path"

# 4. 轻量级虚拟环境（实验性）
# python -m venv --without-pip venv
