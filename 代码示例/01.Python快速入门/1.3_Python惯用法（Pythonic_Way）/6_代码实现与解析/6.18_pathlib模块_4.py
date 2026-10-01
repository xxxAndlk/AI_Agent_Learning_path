# 目录操作 - 创建、遍历、迭代
from pathlib import Path

# 创建目录
Path("new_folder").mkdir()  # 创建单层目录，父目录不存在会抛异常
Path("new_folder").mkdir(parents=True)  # 创建多层目录，自动创建父目录
Path("new_folder").mkdir(parents=True, exist_ok=True)  # 目录存在不报错

# 删除目录和文件
Path("temp.txt").unlink()  # 删除文件
Path("empty_folder").rmdir()  # 删除空目录
# 删除非空目录需使用shutil
import shutil
shutil.rmtree("folder_to_remove")

# 目录遍历 - 迭代目录内容
for item in Path(".").iterdir():  # 遍历当前目录下的所有项
    print(f"{item.name} - {'dir' if item.is_dir() else 'file'}")

# 递归遍历 - 遍历所有子目录
for item in Path(".").rglob("*.py"):  # 递归查找所有.py文件
    print(item)

# 使用glob模式匹配
list(Path(".").glob("*.txt"))    # 当前目录的.txt文件
list(Path(".").glob("**/*.py"))  # 递归所有.py文件（等价rglob）

# 过滤遍历结果
py_files = [p for p in Path("src").rglob("*.py") if not p.name.startswith("_")]

# 获取文件大小和修改时间
file_path = Path("example.txt")
size = file_path.stat().st_size      # 文件大小（字节）
mtime = file_path.stat().st_mtime    # 修改时间（Unix时间戳）

# 转换为datetime
from datetime import datetime
modified = datetime.fromtimestamp(file_path.stat().st_mtime)
