"""
临时文件处理 - 对比Go的os.CreateTemp
"""

import tempfile
import os
from pathlib import Path

# ============ 临时文件 ============
# Go: os.CreateTemp()

# 方式1：NamedTemporaryFile（带名称，可跨进程访问）
# Go: os.CreateTemp()
with tempfile.NamedTemporaryFile(
    mode='w',           # 写入模式
    delete=False,      # 关闭后不删除（需要手动清理）
    suffix='.txt',     # 文件后缀
    prefix='myapp_',   # 文件前缀
    dir='/tmp'         # 指定目录（None使用系统临时目录）
) as f:
    f.write("临时文件内容\n")
    f.write("第二行\n")
    temp_path = f.name
    print(f"临时文件路径: {temp_path}")

# 读取临时文件
with open(temp_path, 'r') as f:
    content = f.read()
    print(f"内容: {content}")

# 手动清理
os.unlink(temp_path)

# 方式2：TemporaryFile（匿名文件，不可见）
# Go: os.CreateTemp() with空名称
with tempfile.TemporaryFile(mode='w+') as f:
    f.write("临时数据")
    f.seek(0)
    print(f.read())  # 可以读取

# ============ 临时目录 ============
# Go: os.MkdirTemp()

with tempfile.TemporaryDirectory(
    suffix='_cache',
    prefix='myapp_',
    dir='/tmp'
) as tmpdir:
    print(f"临时目录: {tmpdir}")
    # 在临时目录中创建文件
    cache_file = Path(tmpdir) / "cache.json"
    cache_file.write_text('{"data": "cached"}')
    # 退出with块时自动删除

# ============ SpooledTemporaryFile（内存临时文件）============
# 大文件可溢出到磁盘

with tempfile.SpooledTemporaryFile(max_size=1024*1024) as f:
    # 数据在内存中，直到超过max_size
    f.write("小数据".encode("utf-8") * 100)
    f.seek(0)
    print(f.read())

# ============ mkstemp（底层函数）============
# 返回文件描述符，需要手动管理

fd, path = tempfile.mkstemp(suffix='.dat')
try:
    os.write(fd, "原始数据".encode("utf-8"))
    os.lseek(fd, 0, 0)
    data = os.read(fd, 100)
    print(data)
finally:
    os.close(fd)
    os.unlink(path)

# ============ 获取系统临时目录 ============
# Go: os.TempDir()

print(f"系统临时目录: {tempfile.gettempdir()}")
print(f"系统临时目录(Path): {tempfile.gettempdir()}")

# 在临时目录创建文件（简写）
cache_file = Path(tempfile.gettempdir()) / "myapp_cache.tmp"
cache_file.write_text("cache data")
