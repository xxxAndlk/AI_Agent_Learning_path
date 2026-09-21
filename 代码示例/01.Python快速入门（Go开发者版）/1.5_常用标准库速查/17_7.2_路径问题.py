# 问题: 文件路径硬编码导致跨平台问题
# 错误: open("C:\\Users\\file.txt")  # Windows only

# 解决1: 使用pathlib（跨平台）
from pathlib import Path
p = Path.home() / "file.txt"  # 自动处理路径分隔符

# 解决2: 使用os.path.join
import os
p = os.path.join(os.path.expanduser("~"), "file.txt")
