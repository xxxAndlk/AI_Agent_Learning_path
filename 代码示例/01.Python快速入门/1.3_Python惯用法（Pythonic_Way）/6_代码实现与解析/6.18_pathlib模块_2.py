# 路径组件访问 - 获取路径的各个部分
config = Path("/home/user/projects/app/config/settings.yaml")
print(config.name)        # settings.yaml - 文件名（最后一部分）
print(config.stem)        # settings - 不含扩展名的文件名
print(config.suffix)      # .yaml - 文件扩展名（包含点）
print(config.suffixes)    # ['yaml'] - 支持多级扩展名如.tar.gz
print(config.parent)      # /home/user/projects/app/config - 父目录Path对象
print(config.parent.parent)  # 向上访问多层
print(config.parts)       # 路径各部分的元组
print(config.anchor)      # 根路径 / 或 Windows的盘符

# 路径属性检查 - 判断路径类型
file_path = Path("example.txt")
file_path.is_file()   # True/False - 是否为普通文件
file_path.is_dir()    # True/False - 是否为目录
file_path.is_symlink()  # True/False - 是否为符号链接
file_path.is_mount()  # True/False - 是否为挂载点

dir_path = Path("my_folder")
print(dir_path.is_dir())  # True

# 存在性检查
Path("example.txt").exists()     # 路径是否存在
Path("/nonexistent").exists()    # False
Path("example.txt").is_file()    # 不存在的文件返回False，不会抛异常

# 路径解析 - 处理.和..以及符号链接，返回绝对路径
Path("./foo/../bar.txt").resolve()  # 解析为绝对路径对象
Path(".").resolve()  # 获取当前工作目录的绝对路径
