import json                        # JSON处理库
import os                          # 操作系统接口
from openai import OpenAI          # OpenAI官方客户端

# 从环境变量读取API密钥初始化客户端（安全做法，避免硬编码）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_current_weather(location, unit="摄氏度"):
    """模拟天气查询函数
    
    参数:
        location: 城市名称
        unit: 温度单位（摄氏度/华氏度）
    返回:
        JSON格式的天气信息
    """
    # 模拟天气数据库
    weather_data = {
        "北京": {"温度": 22, "单位": unit, "描述": "晴朗"},
        "上海": {"温度": 25, "单位": unit, "描述": "多云"},
        "深圳": {"温度": 28, "单位": unit, "描述": "小雨"}
    }
    # 查询并返回JSON格式数据
    return json.dumps(weather_data.get(location, {"温度": "未知", "描述": "未知"}))

def function_calling_example():
    """Function Calling完整流程示例
    
    让模型能够调用外部函数获取信息
    """
    # 定义可用的工具（Responses API 使用扁平格式，参数直接位于工具对象顶层）
    tools = [
        {
            "type": "function",
            "name": "get_current_weather",           # 函数名
            "description": "获取指定城市的当前天气",  # 函数描述
            "parameters": {                          # 参数定义（JSON Schema格式）
                "type": "object",
                "properties": {
                    "location": {                    # 位置参数
                        "type": "string",
                        "description": "城市名称，如北京、上海",
                    },
                    "unit": {                        # 单位参数
                        "type": "string",
                        "enum": ["摄氏度", "华氏度"],  # 枚举值
                    },
                },
                "required": ["location"],            # 必填参数
            },
        }
    ]
    
    # 用户询问天气（Responses API 使用 input 列表承载对话）
    input_list = [{"role": "user", "content": "今天北京的天气怎么样？"}]
    
    # 第一次调用：让模型决定是否需要调用函数
    response = client.responses.create(
        model="gpt-5.4-mini",
        input=input_list,
        tools=tools,                       # 提供可用工具
        tool_choice="auto",                # 自动决定是否调用工具
    )
    
    # 模型的函数调用放在 response.output 列表中（type 为 function_call）
    function_calls = [
        item for item in response.output if item.type == "function_call"
    ]
    
    # 检查模型是否决定调用函数
    if function_calls:
        # 可用的函数映射表
        available_functions = {
            "get_current_weather": get_current_weather,
        }
        
        # 将模型输出（含函数调用项）追加到输入历史
        input_list += response.output
        
        # 执行每个函数调用
        for function_call in function_calls:
            function_name = function_call.name        # 获取函数名
            function_to_call = available_functions[function_name]  # 获取函数
            function_args = json.loads(function_call.arguments)  # 解析参数
            
            # 调用函数并获取结果
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            
            # 将函数结果以 function_call_output 形式追加回输入
            input_list.append(
                {
                    "type": "function_call_output",        # 标记为函数结果
                    "call_id": function_call.call_id,      # 对应的调用ID
                    "output": function_response,           # 函数返回结果
                }
            )
        
        # 第二次调用：让模型基于函数结果生成最终回答
        second_response = client.responses.create(
            model="gpt-5.4-mini",
            input=input_list,
        )
        print("Function Calling结果:", second_response.output_text)

if __name__ == "__main__":
    # 需要先初始化client
    # function_calling_example()
    print("请先初始化OpenAI客户端后再运行")
