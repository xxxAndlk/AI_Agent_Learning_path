import itertools

# 场景1：跳过前N个元素后处理
data = range(100)
remaining = itertools.islice(data, 10, None)
processed = [x * 2 for x in remaining]
print(processed[:5])  # [20, 22, 24, 26, 28]

# 场景2：从无限迭代器中取元素
evens = itertools.count(0, 2)
first_10_evens = list(itertools.islice(evens, 10))
print(first_10_evens)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# 场景3：分页处理
def paginate(iterable, page_size):
    """分页处理迭代器"""
    it = iter(iterable)
    while True:
        page = list(itertools.islice(it, page_size))
        if not page:
            break
        yield page

items = range(25)
for i, page in enumerate(paginate(items, 7)):
    print(f"第{i+1}页: {page}")
# 第1页: [0, 1, 2, 3, 4, 5, 6]
# 第2页: [7, 8, 9, 10, 11, 12, 13]
# 第3页: [14, 15, 16, 17, 18, 19, 20]
# 第4页: [21, 22, 23, 24]
