# 问题代码
def bad_generator():
    yield 1
    raise ValueError("Error!")
    yield 2  # 永远不会执行

# 解决方案：使用try-finally确保资源清理
def good_generator():
    try:
        yield 1
        yield 2
    finally:
        print("Cleanup")  # 即使异常也会执行
