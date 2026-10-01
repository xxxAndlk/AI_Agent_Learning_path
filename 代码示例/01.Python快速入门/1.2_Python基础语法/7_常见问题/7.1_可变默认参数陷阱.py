def add_item(item, items=[]):  # 危险！
    items.append(item)
    return items

print(add_item("a"))  # ['a']
print(add_item("b"))  # ['a', 'b']  # 不是预期的['b']！
