from contextlib import contextmanager, closing

# 使用装饰器定义上下文管理器
@contextmanager
def open_file(path, mode='r'):
    f = open(path, mode)
    try:
        yield f
    finally:
        f.close()

# 使用
with open_file('test.txt') as f:
    content = f.read()

# closing: 自动调用close()方法
from urllib.request import urlopen
with closing(urlopen('http://example.com')) as page:
    content = page.read()
