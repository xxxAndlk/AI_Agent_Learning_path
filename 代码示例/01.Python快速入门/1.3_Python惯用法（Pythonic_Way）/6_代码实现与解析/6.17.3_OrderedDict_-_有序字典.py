from collections import OrderedDict

# Python 3.7+ 普通字典已保证顺序，但OrderedDict仍有用途
# 创建有序字典
od = OrderedDict()
od['a'] = 1
od['b'] = 2
od['c'] = 3

# 按插入顺序迭代
for k, v in od.items():
    print(f"{k}: {v}")  # a:1, b:2, c:3

# move_to_end：移动键到指定位置
od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
od.move_to_end('a')        # 移到末尾: b, c, a
od.move_to_end('a', last=False)  # 移到开头: a, b, c

# popitem：弹出最后一项（Python 3.7+也可用于普通字典）
od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
key, value = od.popitem()  # 弹出最后一项: ('c', 3)
key, value = od.popitem(last=False)  # 弹出第一项: ('a', 1)

# 手动调整顺序
def reorder_by_key(od, key_order):
    """按指定顺序重新排列字典"""
    od_new = OrderedDict()
    for key in key_order:
        if key in od:
            od_new[key] = od[key]
    # 添加未指定的键
    for key in od:
        if key not in od_new:
            od_new[key] = od[key]
    return od_new

od = OrderedDict([('z', 1), ('a', 2), ('m', 3)])
reordered = reorder_by_key(od, ['a', 'm', 'z'])
print(list(reordered.keys()))  # ['a', 'm', 'z']
