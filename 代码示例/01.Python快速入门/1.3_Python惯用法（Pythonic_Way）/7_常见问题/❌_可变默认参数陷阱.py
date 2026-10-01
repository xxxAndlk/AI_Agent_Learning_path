# 反模式：可变默认参数
def add_item(item, items=[]):
    items.append(item)
    return items

add_item(1)  # [1]
add_item(2)  # [1, 2] 共享同一个列表！

# 正确做法：使用None作为默认值
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
