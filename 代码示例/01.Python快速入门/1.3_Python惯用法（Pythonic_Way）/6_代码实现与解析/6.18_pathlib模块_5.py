# 路径比较和匹配
p1 = Path("/home/user/file.txt")
p2 = Path("file.txt")
p3 = Path("/home/user/file.txt")

p1 == p3  # False - 路径不同（相对vs绝对）
p1.resolve() == p3.resolve()  # True - 解析后相同

# 不同操作系统的路径比较
from pathlib import PurePath, PurePosixPath, PureWindowsPath

# PurePath - 不执行实际文件系统操作，纯字符串路径处理
pure = PurePath("/home/user/file.txt")
print(pure.parts)  # ('/', 'home', 'user', 'file.txt')

# 跨平台路径处理 - PurePosixPath和PureWindowsPath
posix = PurePosixPath("/home/user/file")
windows = PureWindowsPath("D:\\Users\\file")

# 使用Pure开头适合处理可能来自不同系统的路径字符串
