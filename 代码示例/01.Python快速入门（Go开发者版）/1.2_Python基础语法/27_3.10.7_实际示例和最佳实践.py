# ============ Lambda最佳实践 ============

# 1. 简化数据转换
data = [1, 2, 3, 4, 5]

# 将数据转换为字典
squared_dict = dict(map(lambda x: (x, x**2), data))
print("平方字典:", squared_dict)

# 列表推导式更简洁
squared_dict_comp = {x: x**2 for x in data}
print("平方字典(推导式):", squared_dict_comp)

# 2. 与map()结合
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
print("map平方:", squared)

# 3. 与reduce()结合
from functools import reduce
product = reduce(lambda a, b: a * b, numbers)
print("乘积:", product)

# 4. Lambda作为返回值
def get_comparator(key):
    if key == "name":
        return lambda x, y: (x["name"] > y["name"]) - (x["name"] < y["name"])
    elif key == "age":
        return lambda x, y: (x["age"] > y["age"]) - (x["age"] < y["age"])
    return lambda x, y: 0

users = [
    {"name": "张三", "age": 25},
    {"name": "李四", "age": 22}
]
sorted_by_age = sorted(users, key=lambda u: u["age"])
print("按年龄排序:", [u["name"] for u in sorted_by_age])

# 5. 避免过度使用Lambda
# 好的用法：简洁的转换函数
get_name = lambda user: user.get("name", "未知")

# 不好的用法：过于复杂难以阅读
# 建议：如果逻辑超过3行，用def定义函数
def is_even_positive(x):
    return x > 0 and x % 2 == 0

filtered = list(filter(is_even_positive, numbers))

# 6. Lambda与类型提示（Python 3.5+）
from typing import Callable
add_lambda: Callable[[int, int], int] = lambda a, b: a + b
