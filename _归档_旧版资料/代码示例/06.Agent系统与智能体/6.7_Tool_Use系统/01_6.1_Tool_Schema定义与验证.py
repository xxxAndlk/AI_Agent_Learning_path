"""
Tool Schema定义与验证示例
展示如何定义标准化的工具描述和参数验证
"""

# 导入标准库和第三方库
from typing import Dict, List, Any, Optional, Callable  # 类型提示相关
from dataclasses import dataclass  # 数据类装饰器，简化类定义
import json  # JSON序列化

# ============ 数据类定义 ============

@dataclass
class ToolParameter:
    """工具参数定义类 - 描述单个参数的元数据"""
    name: str                          # 参数名称：参数的唯一标识符
    type: str                          # 参数类型：支持string/number/integer/boolean/array/object
    description: str                   # 参数描述：供LLM理解参数的用途和含义
    required: bool = True              # 是否必填：默认为True，表示该参数必须提供
    default: Any = None                # 默认值：如果未提供参数，则使用此默认值
    enum: Optional[List] = None        # 枚举值：可选，限制参数必须是枚举值之一
    
    def to_schema(self) -> Dict:
        """
        转换为JSON Schema格式
        将ToolParameter对象转换为符合JSON Schema规范的字典
        """
        schema = {
            "type": self.type,         # 设置参数类型
            "description": self.description  # 设置描述
        }
        # 如果存在枚举值，添加到schema中
        if self.enum:
            schema["enum"] = self.enum
        # 如果存在默认值，添加到schema中
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class ToolSchema:
    """工具Schema定义类 - 描述整个工具的元数据"""
    name: str                          # 工具名称：全局唯一标识
    description: str                   # 工具功能描述：说明工具能做什么
    parameters: List[ToolParameter]    # 参数列表：工具需要的参数
    returns: Dict[str, Any] = None     # 返回值描述：说明返回数据的结构
    examples: List[Dict] = None        # 使用示例：帮助LLM理解如何调用
    
    def to_openai_schema(self) -> Dict:
        """
        转换为OpenAI Function Calling格式
        OpenAI的function calling使用特定的格式，需要转换
        """
        properties = {}  # 初始化属性字典
        required = []    # 初始化必填参数列表
        
        # 遍历所有参数，构建properties和required
        for param in self.parameters:
            properties[param.name] = param.to_schema()  # 转换每个参数
            if param.required:  # 如果参数是必填的
                required.append(param.name)  # 添加到required列表
        
        # 返回符合OpenAI规范的格式
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def to_anthropic_schema(self) -> Dict:
        """
        转换为Anthropic格式
        Anthropic的tool use使用不同的格式（input_schema）
        """
        properties = {}
        required = []
        
        # 同样遍历参数构建properties
        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)
        
        # 返回符合Anthropic规范的格式
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }


# ============ 常用工具Schema定义函数 ============

def create_calculator_schema() -> ToolSchema:
    """
    创建计算器工具Schema
    这是一个简单的数学运算工具
    """
    return ToolSchema(
        name="calculator",  # 工具名称
        description="执行基本数学运算，支持加、减、乘、除",  # 功能描述
        parameters=[
            ToolParameter(
                name="expression",  # 参数名
                type="string",      # 字符串类型
                description="数学表达式，例如：'(15 + 25) * 3 / 5'"  # 参数说明
            )
        ],
        returns={"type": "number", "description": "计算结果"},  # 返回值说明
        examples=[  # 使用示例
            {"expression": "15 + 25"},
            {"expression": "100 / 4 * 3"}
        ]
    )


def create_weather_schema() -> ToolSchema:
    """创建天气查询工具Schema"""
    return ToolSchema(
        name="get_weather",
        description="查询指定城市的当前天气信息，包括温度、湿度、天气状况",
        parameters=[
            ToolParameter(
                name="city",
                type="string",
                description="城市名称，如'北京'、'上海'、'New York'"
            ),
            ToolParameter(
                name="unit",
                type="string",
                description="温度单位",
                required=False,  # 可选参数
                default="celsius",  # 默认值
                enum=["celsius", "fahrenheit"]  # 枚举限制
            )
        ],
        returns={
            "type": "object",
            "properties": {
                "temperature": {"type": "number"},
                "humidity": {"type": "number"},
                "condition": {"type": "string"}
            }
        }
    )


def create_search_schema() -> ToolSchema:
    """创建搜索工具Schema"""
    return ToolSchema(
        name="web_search",
        description="在互联网上搜索信息，返回相关结果列表",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="搜索关键词"
            ),
            ToolParameter(
                name="num_results",
                type="integer",
                description="返回结果数量",
                required=False,
                default=5
            )
        ],
        returns={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "snippet": {"type": "string"}
                }
            }
        }
    )


# ============ Schema验证器 ============

class SchemaValidator:
    """Schema验证器 - 验证传入参数是否符合Schema定义"""
    
    @staticmethod
    def validate_parameters(schema: ToolSchema, arguments: Dict) -> tuple:
        """
        验证参数是否符合Schema定义
        
        参数:
            schema: 工具Schema - 工具的定义规范
            arguments: 传入的参数 - 需要验证的参数字典
        返回:
            (is_valid, errors) 元组 - 验证结果和错误列表
        """
        errors = []  # 初始化错误列表
        
        # 第一步：检查必填参数
        # 遍历schema中定义的所有参数
        for param in schema.parameters:
            # 如果是必填参数但不在传入参数中
            if param.required and param.name not in arguments:
                errors.append(f"缺少必填参数: {param.name}")
        
        # 第二步：检查参数类型和枚举值
        # 遍历传入的每个参数
        for param_name, value in arguments.items():
            # 查找schema中对应的参数定义
            param = next((p for p in schema.parameters if p.name == param_name), None)
            if not param:
                errors.append(f"未知参数: {param_name}")  # 传入的参数不在schema中
                continue
            
            # 类型检查：验证参数类型是否正确
            if not SchemaValidator._check_type(value, param.type):
                errors.append(f"参数'{param_name}'类型错误: 期望{param.type}，实际{type(value).__name__}")
            
            # 枚举检查：如果定义了枚举值，验证是否在枚举范围内
            if param.enum and value not in param.enum:
                errors.append(f"参数'{param_name}'值错误: 必须是{param.enum}之一")
        
        # 返回验证结果：没有错误即通过
        return len(errors) == 0, errors
    
    @staticmethod
    def _check_type(value: Any, expected_type: str) -> bool:
        """检查值是否符合期望类型"""
        # 类型映射：将schema类型映射到Python类型
        type_mapping = {
            "string": str,          # 字符串
            "number": (int, float), # 数字（整数或浮点数）
            "integer": int,         # 整数
            "boolean": bool,        # 布尔值
            "array": list,          # 列表
            "object": dict          # 字典
        }
        
        expected = type_mapping.get(expected_type)  # 获取期望的Python类型
        if not expected:  # 如果未知的类型，直接返回True（不做检查）
            return True
        
        return isinstance(value, expected)  # 使用isinstance检查类型


# 使用示例
if __name__ == "__main__":
    # 创建工具Schema
    calculator_schema = create_calculator_schema()
    weather_schema = create_weather_schema()
    
    # 转换为不同格式
    print("=== OpenAI格式 ===")
    print(json.dumps(calculator_schema.to_openai_schema(), ensure_ascii=False, indent=2))
    
    print("\n=== Anthropic格式 ===")
    print(json.dumps(weather_schema.to_anthropic_schema(), ensure_ascii=False, indent=2))
    
    # 验证参数
    print("\n=== 参数验证 ===")
    validator = SchemaValidator()
    
    # 正确的参数
    valid_args = {"expression": "15 + 25"}
    is_valid, errors = validator.validate_parameters(calculator_schema, valid_args)
    print(f"正确参数验证: {'通过' if is_valid else '失败'}")
    
    # 错误的参数
    invalid_args = {"expr": "15 + 25"}  # 参数名错误
    is_valid, errors = validator.validate_parameters(calculator_schema, invalid_args)
    print(f"错误参数验证: {'通过' if is_valid else '失败'}")
    if errors:
        print(f"  错误: {errors}")
