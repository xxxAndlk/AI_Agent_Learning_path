"""
JSON模式约束解码
使用outlines库实现
"""

# 安装: pip install outlines

import outlines
from outlines.models import transformer
import json

# 加载模型
model = transformer("meta-llama/Llama-2-7b-chat-hf")

# 定义JSON Schema
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "employed": {"type": "boolean"}
    },
    "required": ["name", "age"]
}

# 创建JSON引导的生成器
json_generator = outlines.generate.json(model, json_schema)

# 生成
prompt = "请提供你的个人信息："
result = json_generator(prompt)

print(result)
# 输出: {"name": "张三", "age": 30, "email": "zhangsan@example.com", ...}

# 复杂JSON Schema示例
complex_schema = {
    "type": "object",
    "properties": {
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "role": {"enum": ["admin", "user", "guest"]}
                },
                "required": ["id", "name"]
            }
        },
        "total": {"type": "integer"}
    },
    "required": ["users"]
}

complex_generator = outlines.generate.json(model, complex_schema)
result = complex_generator("列出系统用户：")
