# ============ 过滤操作与Lambda ============

# 准备测试数据
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
strings = ["apple", "banana", "cherry", "date", "elderberry"]
products = [
    {"name": "iPhone", "price": 999, "category": "phone"},
    {"name": "MacBook", "price": 1999, "category": "laptop"},
    {"name": "iPad", "price": 799, "category": "tablet"},
    {"name": "AirPods", "price": 199, "category": "audio"}
]

# 使用filter()函数过滤
# filter(function, iterable)返回满足条件的元素

# 过滤偶数
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("偶数:", evens)  # [2, 4, 6, 8, 10]

# 过滤大于5的数
greater_than_5 = list(filter(lambda x: x > 5, numbers))
print("大于5:", greater_than_5)  # [6, 7, 8, 9, 10]

# 过滤以字母'a'开头的字符串
starts_with_a = list(filter(lambda s: s.startswith("a"), strings))
print("以a开头:", starts_with_a)  # ['apple']

# 过滤价格低于1000的产品
cheap_products = list(filter(lambda p: p["price"] < 1000, products))
print("低价产品:", [p["name"] for p in cheap_products])  # ['iPad', 'AirPods']

# 使用列表推导式实现相同功能（更Pythonic）
evens_comprehension = [x for x in numbers if x % 2 == 0]
print("列表推导式-偶数:", evens_comprehension)
