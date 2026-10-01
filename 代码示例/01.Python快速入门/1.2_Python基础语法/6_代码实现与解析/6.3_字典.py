# ============ 字典操作 ============
# 
person = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}

# 空字典
# 
empty_dict = {}

# 访问值
# 
name = person["name"]           # 访问（如果key不存在会报错）
name = person.get("name")       # 安全访问
name = person.get("name", "未知") # 提供默认值

# 添加/修改
# 
person["email"] = "zhangsan@example.com"

# 删除
# 
del person["email"]
email = person.pop("email", None)  # 删除并返回值

# 检查key是否存在
# 
if "name" in person:
    print("存在name字段")

# 遍历
# 
for key, value in person.items():
    print(f"{key}: {value}")

# 只遍历keys
for key in person.keys():
    print(key)

# 只遍历values
for value in person.values():
    print(value)

# 长度
count = len(person)
