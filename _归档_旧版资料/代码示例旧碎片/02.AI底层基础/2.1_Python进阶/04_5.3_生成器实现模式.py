import json

# 生成器表达式（内存高效）
squares = (x**2 for x in range(1000000))  # 不占用大量内存

# 生成器管道
def read_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip()

def filter_comments(lines):
    for line in lines:
        if not line.startswith('#'):
            yield line

def parse_json(lines):
    for line in lines:
        yield json.loads(line)

# 链式处理
pipeline = parse_json(filter_comments(read_lines('data.txt')))

# yield from 委托生成器
def chain(*iterables):
    for iterable in iterables:
        yield from iterable  # 委托给子生成器
