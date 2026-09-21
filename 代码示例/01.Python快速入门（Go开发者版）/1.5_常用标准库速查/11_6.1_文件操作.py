"""
文件操作示例 - 对比Go实现
"""

import os
import shutil
from pathlib import Path

# ============ 文件读写 ============
# Go: os.ReadFile() / os.WriteFile()

# Python: 读取文件（推荐with语句）
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()  # 读取全部
    lines = f.readlines()  # 读取为列表

# Python: 写入文件
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")
    f.writelines(["Line 1\n", "Line 2\n"])

# ============ 目录操作 ============
# Go: os.MkdirAll() / os.RemoveAll()

# 创建目录
os.makedirs("path/to/dir", exist_ok=True)  # 递归创建

# 删除目录
shutil.rmtree("path/to/dir")  # 递归删除
os.rmdir("empty_dir")  # 删除空目录

# ============ 文件信息 ============
# Go: os.Stat()

from pathlib import Path

p = Path("file.txt")
if p.exists():
    print(f"Size: {p.stat().st_size} bytes")
    print(f"Modified: {p.stat().st_mtime}")

# ============ 遍历目录 ============
# Go: filepath.WalkDir()

# 方法1: os.walk
for root, dirs, files in os.walk("/path"):
    for file in files:
        filepath = os.path.join(root, file)
        print(filepath)

# 方法2: pathlib（更现代）
for filepath in Path("/path").rglob("*.py"):  # 递归查找.py文件
    print(filepath)
