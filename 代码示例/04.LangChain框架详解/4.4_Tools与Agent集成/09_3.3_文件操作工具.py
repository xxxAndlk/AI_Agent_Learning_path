import json
from langchain_core.tools import tool

# 定义JSON数据的结构
json_data = '''
{
    "users": [
        {"name": "张三", "age": 28},
        {"name": "李四", "age": 32}
    ]
}
'''

@tool
def extract_user_names(data: str) -> str:
    """从JSON数据中提取所有用户的名字"""
    try:
        return ", ".join(u["name"] for u in json.loads(data)["users"])
    except Exception as e:
        return f"解析失败: {e}"

result = extract_user_names.invoke(json_data)
print(result)
