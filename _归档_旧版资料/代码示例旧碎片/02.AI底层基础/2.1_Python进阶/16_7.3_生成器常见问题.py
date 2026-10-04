# 问题代码
def read_file(filename):
    f = open(filename)
    for line in f:
        yield line
    f.close()  # 如果生成器提前退出，不会关闭文件

# 解决方案：使用try-finally或with
def read_file(filename):
    with open(filename) as f:  # ✅ 确保文件关闭
        for line in f:
            yield line
