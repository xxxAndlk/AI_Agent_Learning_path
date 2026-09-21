import sys

# 查看模块搜索路径（类似Go的GOPATH）
print(sys.path)
# ['', '/usr/lib/python3.12', '/usr/lib/python3.12/lib-dynload', ...]

# 添加自定义路径
sys.path.insert(0, '/my/custom/path')
