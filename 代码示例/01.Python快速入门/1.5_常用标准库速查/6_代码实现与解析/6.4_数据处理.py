"""
数据处理示例
"""

import json
import csv
from datetime import datetime, timedelta

# ============ JSON处理 ============

# 复杂对象序列化
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def to_dict(self):
        return {"name": self.name, "age": self.age}

person = Person("张三", 25)
json_str = json.dumps(person.to_dict(), ensure_ascii=False, indent=2)

# ============ CSV处理 ============

# 写入CSV
with open("data.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Age", "City"])
    writer.writerow(["张三", 25, "北京"])
    writer.writerow(["李四", 30, "上海"])

# 读取CSV
with open("data.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['Name']}: {row['Age']}")

# ============ 日期时间计算 ============

# 当前时间
now = datetime.now()

# 时间差
diff = timedelta(days=7, hours=3)
future = now + diff

# 时间戳转换
timestamp = datetime.now().timestamp()
dt_from_ts = datetime.fromtimestamp(timestamp)

# 格式化输出
print(now.strftime("今天是%Y年%m月%d日"))
