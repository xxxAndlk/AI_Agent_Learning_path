# 与os.path对比 - pathlib是更现代的选择
import os
from pathlib import Path

# 传统方式（os.path）
os.path.join("dir", "file.txt")  # 手动拼接
os.path.exists("file.txt")       # 检查存在
os.path.isfile("file.txt")       # 检查是否为文件
os.path.isdir("folder")          # 检查是否为目录
os.path.basename(path)           # 获取文件名
os.path.dirname(path)            # 获取目录名
os.path.splitext(path)           # 分离扩展名

# pathlib方式（更直观）
path = Path("dir") / "file.txt"  # 使用/操作符
path.exists()
path.is_file()
path.is_dir()
path.name          # 文件名
path.parent        # 父目录
path.suffix        # 扩展名
