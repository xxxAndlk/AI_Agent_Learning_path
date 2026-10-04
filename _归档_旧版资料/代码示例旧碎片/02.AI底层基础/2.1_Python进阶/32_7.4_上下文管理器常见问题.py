# 问题代码
@contextmanager
def bad_manager():
    yield "value"
    # 如果yield前发生异常，finally块不执行
    cleanup()

# 解决方案：使用try-finally
@contextmanager
def good_manager():
    try:
        yield "value"
    finally:
        cleanup()  # 无论是否异常都会执行
