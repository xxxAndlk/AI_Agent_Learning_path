# 导入Path类
from pathlib import Path

# 创建Path对象 - 表示文件系统中的路径
p = Path(".")  # 当前目录
p = Path("/home/user/projects")  # 绝对路径
p = Path("D:/data/demo/py_AI_doc")  # Windows路径自动处理

# 路径拼接 - 使用 / 操作符（这是pathlib最优雅的特性）
base = Path("/home/user")
config = base / "config" / "app.yaml"  # / 操作符自动处理路径分隔符

# 兼容Windows和Unix
# Unix: /home/user/config/app.yaml
# Windows: D:\home\user\config\app.yaml
