# with语句自动处理资源的获取和释放
with open('file.txt', 'r') as f:
    content = f.read()
# 文件自动关闭，即使发生异常
