from collections import ChainMap

# 创建ChainMap
dict1 = {'a': 1, 'b': 2}
dict2 = {'b': 3, 'c': 4}
dict3 = {'c': 5, 'd': 6}

cm = ChainMap(dict1, dict2, dict3)

# 查询：从左到右查找
print(cm['a'])  # 1（只在dict1中）
print(cm['b'])  # 2（dict1中有，返回第一个找到的）
print(cm['c'])  # 4（dict1没有，dict2有）
print(cm['d'])  # 6（dict1, dict2都没有，dict3有）

# 遍历所有键值对
for key, value in cm.items():
    print(f"{key}: {value}")
# 输出顺序：dict1, dict2, dict3中所有不重复的键

# 遍历所有键
print(list(cm.keys()))  # ['a', 'b', 'c', 'd']
print(list(cm.values()))  # [1, 2, 4, 6]

# 长度（去重后的键数）
print(len(cm))  # 4

# 成员检查
print('a' in cm)  # True
print('z' in cm)  # False

# 修改：只影响第一个字典
cm['a'] = 100
print(dict1['a'])  # 100（dict1被修改）
print(cm['a'])     # 100

# 添加新键：添加到第一个字典
cm['e'] = 7
print(dict1)  # {'a': 100, 'b': 2, 'e': 7}

# 删除：删除第一个字典中的键
del cm['e']
print(dict1)  # {'a': 100, 'b': 2}

# new_child：创建新的ChainMap（前面的字典作为新子图）
cm2 = cm.new_child({'f': 8})
print(cm2['f'])  # 8
print(cm2['a'])  # 100（回退查找）

# maps属性：访问底层字典列表
print(cm.maps)  # [{'a': 100, 'b': 2}, {'b': 3, 'c': 4}, {'c': 5, 'd': 6}]

# 重建ChainMap（当底层字典变化时）
# ChainMap会反映底层字典的变化
dict1['g'] = 9
print(cm['g'])  # 9（自动反映）
