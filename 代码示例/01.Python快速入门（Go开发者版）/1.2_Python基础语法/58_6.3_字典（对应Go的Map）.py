# ============ 字典操作（对比Go的Map） ============
# Go: m := make(map[string]int)
# Python:
person = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}

# 空字典
# Go: m := make(map[string]string)
# Python:
empty_dict = {}

# 访问值
# Go: name := m["name"]
# Python:
name = person["name"]           # 访问（如果key不存在会报错）
name = person.get("name")       # 安全访问（不存在返回None，类似Go的comma ok）
name = person.get("name", "未知") # 提供默认值

# 添加/修改
# Go: m["email"] = "zhangsan@example.com"
# Python:
person["email"] = "zhangsan@example.com"

# 删除
# Go: delete(m, "email")
# Python:
del person["email"]
email = person.pop("email", None)  # 删除并返回值

# 检查key是否存在
# Go: if val, ok := m["key"]; ok { ... }
# Python:
if "name" in person:
    print("存在name字段")

# 遍历
# Go: for k, v := range m { ... }
# Python:
for key, value in person.items():
    print(f"{key}: {value}")

# 只遍历keys
for key in person.keys():
    print(key)

# 只遍历values
for value in person.values():
    print(value)

# 长度
# Go: len(m)
count = len(person)
