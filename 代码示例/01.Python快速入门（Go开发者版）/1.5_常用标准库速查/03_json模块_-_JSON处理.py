import json

# Python对象 → JSON字符串
# Go: json.Marshal()
data = {"name": "张三", "age": 25}
json_str = json.dumps(data, ensure_ascii=False)
print(json_str)  # {"name": "张三", "age": 25}

# JSON字符串 → Python对象  
# Go: json.Unmarshal()
parsed = json.loads(json_str)
print(parsed["name"])  # 张三

# 读写文件
# Go: os.WriteFile() + json.Marshal()
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
