# 自定义上下文管理器
import time
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    """计时上下文管理器"""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name} 耗时: {elapsed:.4f}秒")

# 使用
with timer("数据处理"):
    process_large_dataset()

# 文件批量处理
@contextmanager
def multi_file_writer(*filenames):
    files = [open(f, 'w') for f in filenames]
    try:
        yield files
    finally:
        for f in files:
            f.close()
