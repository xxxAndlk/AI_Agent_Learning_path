from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_core.tools import tool

class WeatherInput(BaseModel):
    """天气查询输入参数"""
    city: str = Field(description="城市名称，如北京、上海")
    country: str = Field(default="中国", description="国家或地区")
    unit: str = Field(default="celsius", description="温度单位: celsius 或 fahrenheit")

@tool
def get_weather(input: WeatherInput) -> str:
    """查询指定城市的天气信息"""
    city = input.city
    country = input.country
    unit = input.unit
    
    # 模拟天气数据
    temp = 25 if unit == "celsius" else 77
    condition = "晴朗"
    
    return f"{city}, {country}: {condition}, 温度: {temp}°{'C' if unit == 'celsius' else 'F'}"

# 使用工具
result = get_weather.invoke({"city": "上海", "country": "中国", "unit": "celsius"})
print(result)
