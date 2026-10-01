# 练习 3 参考答案：JSON 存取
# 把待办列表 json.dump 存进文件，再 json.load 读回来

import json
import tempfile
from pathlib import Path

todos = ["买牛奶", "写第 11 课练习", "跑步半小时", "给爸妈打电话"]

# 文件放系统临时文件夹，不往课目录留数据文件；ensure_ascii=False 让中文保持中文
path = Path(tempfile.gettempdir()) / "python_lesson11_todo.json"

with open(path, "w", encoding="utf-8") as f:
    json.dump(todos, f, ensure_ascii=False, indent=2)
print(f"已存入 {path}")

with open(path, "r", encoding="utf-8") as f:
    loaded = json.load(f)

print("读回来的待办：")
for i, t in enumerate(loaded, start=1):
    print(f"{i}. {t}")
