import os
from pydantic import BaseModel, Field  # Pydantic数据验证库
from typing import List                # 类型提示
import json                            # JSON处理
from openai import OpenAI              # OpenAI客户端

# 从环境变量读取API密钥初始化客户端（安全做法，避免硬编码）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 定义用户数据模型
class User(BaseModel):
    """用户数据模型：定义期望的输出结构"""
    name: str = Field(description="用户的姓名")           # 姓名字段
    age: int = Field(description="用户的年龄")            # 年龄字段
    hobbies: List[str] = Field(description="用户的爱好列表")  # 爱好列表

def structured_output_example():
    """结构化输出示例
    
    强制模型输出符合预定义格式的JSON数据
    """
    # 提示模型生成用户信息
    prompt = "请生成一个用户信息，包含姓名、年龄和3个爱好。"
    
    # 使用response_format约束输出格式
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",     # 使用JSON Schema约束
            "json_schema": {
                "name": "user_schema", # Schema名称
                "schema": User.model_json_schema()  # 从Pydantic模型生成Schema
            }
        }
    )
    
    # 解析JSON响应
    user_json = json.loads(response.choices[0].message.content)
    
    # 使用Pydantic验证并解析数据
    user = User(**user_json)
    
    # 打印结构化结果
    print("结构化输出结果:")
    print(f"姓名: {user.name}")
    print(f"年龄: {user.age}")
    print(f"爱好: {', '.join(user.hobbies)}")

def json_mode_example():
    """JSON Mode：强制模型输出有效的JSON格式
    
    适用于需要结构化数据但不需要严格Schema的场景
    """
    prompt = """
    请分析以下产品评价，并以JSON格式返回分析结果：
    评价："这款手机电池续航很差，但拍照效果非常出色，性价比还可以。"
    
    要求返回以下字段：
    - sentiment: 整体情感（positive/negative/neutral）
    - aspects: 提到的各个方面列表
    - rating: 预估评分（1-5）
    """
    
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}  # 启用JSON模式
    )
    
    # 解析JSON响应
    result = json.loads(response.choices[0].message.content)
    print("JSON Mode结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    # 需要先初始化client后运行
    # structured_output_example()
    # json_mode_example()
    print("请先初始化OpenAI客户端后再运行")
