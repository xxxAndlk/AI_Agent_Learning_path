# 数据清洗管道
data = [
    {"name": "Alice", "age": "30", "city": "Beijing"},
    {"name": "Bob", "age": "25", "city": "Shanghai"},
    {"name": "Charlie", "age": "35", "city": "Guangzhou"},
]

# Pythonic方式：链式处理
result = [
    {**item, "age": int(item["age"])}
    for item in data
    if int(item["age"]) > 25
]

# 分组统计
from itertools import groupby
sorted_data = sorted(data, key=lambda x: x["city"])
for city, group in groupby(sorted_data, key=lambda x: x["city"]):
    print(f"{city}: {len(list(group))} people")
