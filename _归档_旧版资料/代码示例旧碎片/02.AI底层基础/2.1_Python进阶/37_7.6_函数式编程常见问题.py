# 问题
def bad_func(items=[]):
    items.append(1)
    return items

# 解决方案
def good_func(items=None):
    if items is None:
        items = []
    items.append(1)
    return items
