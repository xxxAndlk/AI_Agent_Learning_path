# 文件操作 - Path对象直接提供文件读写方法
from pathlib import Path

# 读取文件内容
content = Path("example.txt").read_text()  # 读取全部文本
content = Path("example.txt").read_bytes()  # 读取为字节

# 写入文件内容（自动创建父目录）
Path("output.txt").write_text("Hello, World!")  # 写入文本
Path("data.bin").write_bytes(b"\x00\x01\x02")   # 写入字节

# 读取 JSON 文件
import json
config = json.loads(Path("config.json").read_text())

# 写入 JSON 文件
data = {"name": "Alice", "age": 30}
Path("data.json").write_text(json.dumps(data, indent=2))

# 文件复制（Python 3.8+）
import shutil
shutil.copy2("source.txt", "dest.txt")  # 使用os函数
# 或使用Path
Path("source.txt").replace("dest.txt")  # 注意：会覆盖目标
