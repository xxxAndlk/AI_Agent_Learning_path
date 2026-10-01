# 11. with语句资源管理
# 不推荐
# f = open('file.txt')
# try:
#     content = f.read()
# finally:
#     f.close()

# 推荐（Pythonic）
with open('file.txt') as f:
    content = f.read()
# 文件自动关闭
