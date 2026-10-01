import dis

def add(a, b):
    return a + b

# 查看字节码
dis.dis(add)
