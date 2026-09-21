import os

# 环境变量
# Go: os.Getenv("PATH")
path = os.getenv("PATH")           # 获取环境变量
os.environ["MY_VAR"] = "value"     # 设置环境变量

# 文件路径操作
# Go: filepath.Join()
full_path = os.path.join("dir", "file.txt")
abs_path = os.path.abspath("./file.txt")
exists = os.path.exists("file.txt")
