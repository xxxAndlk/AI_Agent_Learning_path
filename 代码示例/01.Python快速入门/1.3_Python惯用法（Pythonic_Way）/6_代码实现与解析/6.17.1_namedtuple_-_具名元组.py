from collections import namedtuple

# 定义具名元组类型
# 语法：namedtuple('类型名', ['字段1', '字段2', ...])
Point = namedtuple('Point', ['x', 'y'])

# 创建实例
p1 = Point(10, 20)
p2 = Point(x=5, y=15)

# 访问方式1：通过属性名（推荐）
print(p1.x)        # 10
print(p1.y)        # 20

# 访问方式2：通过索引
print(p1[0])       # 10
print(p1[1])       # 20

# 访问方式3：解包
x, y = p1
print(x, y)        # 10 20

# 具名元组是不可变的
# p1.x = 30  # TypeError: can't set attribute

# 转换为字典
print(p1._asdict())  # {'x': 10, 'y': 20}

# 替换某些字段（返回新实例）
p3 = p1._replace(x=100)
print(p3)           # Point(x=100, y=20)

# 使用_make从可迭代对象创建
data = [30, 40]
p4 = Point._make(data)
print(p4)           # Point(x=30, y=40)
