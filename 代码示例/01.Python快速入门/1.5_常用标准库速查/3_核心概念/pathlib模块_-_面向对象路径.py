from pathlib import Path

# 创建路径对象
p = Path("/home/user/documents/file.txt")

# 路径操作
print(p.name)       # file.txt（文件名）
print(p.parent)     # /home/user/documents（父目录）
print(p.suffix)     # .txt（扩展名）
print(p.stem)       # file（不含扩展名的文件名）

# 路径拼接（比os.path更直观）
new_path = p.parent / "subdir" / "newfile.txt"
