from collections import Counter

# 创建计数器
c1 = Counter()  # 空计数器
c2 = Counter(['a', 'b', 'a', 'c', 'a'])  # 从可迭代对象
c3 = Counter({'a': 3, 'b': 1})  # 从字典
c4 = Counter(a=3, b=1, c=0)  # 从关键字参数

print(c2)  # Counter({'a': 3, 'b': 1, 'c': 1})

# 访问不存在的元素返回0，不会抛出异常
print(c2['d'])  # 0

# 修改计数
c2['a'] = 5  # 修改
c2['b'] += 1  # 增加
del c2['c']  # 删除（完全移除）

# elements()：返回所有元素（重复次数等于计数）
c = Counter(['a', 'b', 'a', 'c', 'a'])
print(list(c.elements()))  # ['a', 'a', 'a', 'b', 'c']，顺序不确定

# most_common(n)：返回最常见的n个元素
c = Counter('abracadabra')
print(c.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]

# subtract()：相减
c1 = Counter(['a', 'b', 'c'])
c2 = Counter('abcbb')
c1.subtract(c2)
print(c1)  # Counter({'a': 0, 'b': -1, 'c': -1})

# 数学运算
c1 = Counter(['a', 'b', 'c', 'a'])
c2 = Counter(['a', 'b', 'd'])

# 加法（并集，取较大值）
print(c1 + c2)  # Counter({'a': 2, 'b': 2, 'c': 1, 'd': 1})

# 减法（差集）
print(c1 - c2)  # Counter({'c': 1})

# 交集（取较小值）
print(c1 & c2)  # Counter({'a': 1, 'b': 1})

# 并集（取较大值，等价于加法）
print(c1 | c2)  # Counter({'a': 2, 'b': 2, 'c': 1, 'd': 1})

# update()：合并计数
c = Counter(['a', 'b'])
c.update(['a', 'a', 'c'])
print(c)  # Counter({'a': 3, 'b': 1, 'c': 1})

# 统计字符出现频率
text = "hello world"
char_count = Counter(text.replace(' ', ''))
print(char_count.most_common())  # [('l', 3), ('o', 2), ('h', 1), ...]
