"""
LangChain Agent示例
展示如何使用LangChain构建具有工具调用能力的Agent
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

# ============ 模拟LLM和工具组件 ============

@dataclass
class Message:
    """消息类：用于存储对话中的消息记录"""
    role: str              # 角色: system/user/assistant/tool
    content: str           # 消息内容
    name: Optional[str] = None  # 工具名称（仅tool角色使用）

class MockLLM:
    """模拟LLM类（实际使用时替换为真实LLM）
    
    此类模拟大型语言模型的响应行为，
    在实际生产环境中应替换为真实的API调用
    """
    
    def __init__(self, model_name: str = "gpt-5.4"):
        """初始化模拟LLM
        
        参数:
            model_name: 模型名称，用于标识使用的LLM
        """
        self.model_name = model_name
        self.call_count = 0  # 记录调用次数，用于调试
    
    def invoke(self, messages: List[Message]) -> str:
        """调用LLM生成响应
        
        参数:
            messages: 消息列表，包含对话历史
        返回:
            生成的响应文本
        """
        self.call_count += 1
        
        # 获取最后一条消息内容作为输入
        last_message = messages[-1].content if messages else ""
        
        # 检测是否需要调用工具 - 简单的关键词匹配
        # 实际应用中，LLM会根据上下文自行判断
        if "计算" in last_message or "+" in last_message:
            # 返回JSON格式的工具调用指示
            return json.dumps({
                "thought": "用户需要计算，我应该使用计算器工具",
                "action": "calculator",
                "action_input": {"expression": "3 + 5"}
            })
        elif "天气" in last_message:
            return json.dumps({
                "thought": "用户想查天气，我应该使用天气工具",
                "action": "get_weather",
                "action_input": {"city": "北京"}
            })
        else:
            # 普通对话，直接返回回复
            return f"这是一个模拟回复：关于'{last_message}'的回答"

class Tool:
    """工具基类：所有工具的抽象基类
    
    定义工具的基本接口，所有具体工具都应继承此类
    """
    
    def __init__(self, name: str, description: str):
        """初始化工具
        
        参数:
            name: 工具名称，用于唯一标识
            description: 工具描述，供LLM理解工具用途
        """
        self.name = name
        self.description = description
    
    def run(self, *args, **kwargs) -> str:
        """运行工具（子类实现）
        
        此方法由子类具体实现，执行实际的工具逻辑
        """
        raise NotImplementedError

class CalculatorTool(Tool):
    """计算器工具：执行数学计算
    
    继承Tool基类，实现具体的计算功能
    """
    
    def __init__(self):
        """初始化计算器"""
        super().__init__(
            name="calculator",
            description="执行数学计算。输入数学表达式，返回计算结果。"
        )
    
    def run(self, expression: str) -> str:
        """执行计算
        
        参数:
            expression: 数学表达式（如 "3 + 5"）
        返回:
            计算结果字符串
        """
        try:
            # 注意：实际应用中应使用更安全的表达式解析
            # eval()存在安全风险，生产环境应使用专门的数学表达式解析库
            result = eval(expression)  # 执行数学表达式
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"

class WeatherTool(Tool):
    """天气查询工具：查询指定城市的天气信息
    
    模拟天气查询功能，实际应用中应调用真实天气API
    """
    
    def __init__(self):
        """初始化天气工具"""
        super().__init__(
            name="get_weather",
            description="查询指定城市的天气信息。输入城市名称，返回天气详情。"
        )
        # 模拟天气数据 - 实际应用中应从API获取
        self.weather_data = {
            "北京": {"temp": 25, "condition": "晴天", "humidity": 45},
            "上海": {"temp": 28, "condition": "多云", "humidity": 60},
            "深圳": {"temp": 30, "condition": "小雨", "humidity": 75}
        }
    
    def run(self, city: str) -> str:
        """查询天气
        
        参数:
            city: 城市名称
        返回:
            天气信息字符串
        """
        if city in self.weather_data:
            data = self.weather_data[city]
            return f"{city}天气: {data['condition']}，温度{data['temp']}°C，湿度{data['humidity']}%"
        return f"未找到{city}的天气信息"

class SearchTool(Tool):
    """搜索工具：搜索网络信息
    
    模拟搜索功能，实际应用中应调用真实搜索引擎API
    """
    
    def __init__(self):
        """初始化搜索工具"""
        super().__init__(
            name="search",
            description="搜索网络信息。输入搜索关键词，返回相关结果。"
        )
    
    def run(self, query: str) -> str:
        """执行搜索
        
        参数:
            query: 搜索关键词
        返回:
            搜索结果字符串
        """
        # 模拟搜索结果 - 实际应用中应调用真实搜索API
        return f"搜索'{query}'的结果：找到3条相关信息..."

# ============ LangChain风格Agent实现 ============

class LangChainAgent:
    """LangChain风格的Agent实现
    
    实现ReAct（Reasoning + Acting）模式：
    1. 思考（Thought）：分析当前情况
    2. 行动（Action）：选择并执行工具
    3. 观察（Observation）：获取执行结果
    4. 循环直到完成任务
    
    这是LangChain Agent的核心工作流程
    """
    
    def __init__(self, llm: MockLLM, tools: List[Tool]):
        """初始化Agent
        
        参数:
            llm: LLM实例，用于生成响应和决策
            tools: 可用工具列表，Agent可以调用这些工具
        """
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}  # 工具名称到工具的映射，便于快速查找
        self.messages: List[Message] = []  # 对话历史，维护完整的对话上下文
        self.max_iterations = 5  # 最大迭代次数，防止无限循环
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词
        
        告诉Agent它可以使用的工具和输出格式
        这是引导LLM正确使用工具的关键
        """
        # 生成所有工具的描述列表
        tool_descriptions = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
        
        # 返回格式化的系统提示词
        return f"""你是一个智能助手，可以使用以下工具：
{tool_descriptions}

当你需要使用工具时，请以JSON格式输出：
{{
    "thought": "你的思考过程",
    "action": "工具名称",
    "action_input": {{工具参数}}
}}

当你有了最终答案时，直接用自然语言回答。"""
    
    def add_message(self, role: str, content: str, name: str = None):
        """添加消息到历史
        
        参数:
            role: 消息角色（system/user/assistant/tool）
            content: 消息内容
            name: 工具名称（可选，仅tool角色使用）
        """
        self.messages.append(Message(role=role, content=content, name=name))
    
    def run(self, user_input: str) -> str:
        """执行Agent主循环
        
        实现ReAct循环：推理→行动→观察→继续
        参数:
            user_input: 用户输入
        返回:
            最终响应
        """
        # 初始化：添加系统提示和用户消息
        if not self.messages:
            self.add_message("system", self._build_system_prompt())
        
        self.add_message("user", user_input)
        
        # ReAct循环 - 核心执行逻辑
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            # 步骤1：调用LLM获取响应
            response = self.llm.invoke(self.messages)
            self.add_message("assistant", response)
            
            # 步骤2：尝试解析为工具调用
            try:
                parsed = json.loads(response)
                
                # 检查是否包含action字段
                if "action" in parsed:
                    # 需要调用工具
                    tool_name = parsed["action"]
                    tool_input = parsed["action_input"]
                    
                    # 验证工具是否存在
                    if tool_name in self.tools:
                        # 执行工具
                        tool = self.tools[tool_name]
                        # 根据参数类型选择调用方式
                        if isinstance(tool_input, dict):
                            result = tool.run(**tool_input)
                        else:
                            result = tool.run(tool_input)
                        
                        # 添加工具结果到消息历史，供LLM参考
                        self.add_message("tool", result, name=tool_name)
                        continue  # 继续循环，让LLM处理工具结果
                    else:
                        return f"错误：未知工具 '{tool_name}'"
                
            except json.JSONDecodeError:
                # 不是JSON格式，说明是最终回答，直接返回
                pass
            
            # 没有工具调用，返回响应
            return response
        
        return "达到最大迭代次数，任务未能完成"

# ============ 使用示例 ============

def demo_langchain_agent():
    """演示LangChain Agent的使用"""
    
    print("=" * 50)
    print("LangChain Agent 演示")
    print("=" * 50)
    
    # 创建LLM和工具实例
    llm = MockLLM()
    tools = [
        CalculatorTool(),   # 计算器工具
        WeatherTool(),      # 天气工具
        SearchTool()        # 搜索工具
    ]
    
    # 创建Agent实例
    agent = LangChainAgent(llm=llm, tools=tools)
    
    # 测试1：计算任务
    print("\n【测试1：计算任务】")
    print("用户：计算3 + 5等于多少？")
    result = agent.run("计算3 + 5等于多少？")
    print(f"Agent：{result}")
    
    # 测试2：天气查询 - 需要新建Agent实例以重置对话历史
    agent = LangChainAgent(llm=llm, tools=tools)
    
    print("\n【测试2：天气查询】")
    print("用户：北京今天天气怎么样？")
    result = agent.run("北京今天天气怎么样？")
    print(f"Agent：{result}")

if __name__ == "__main__":
    demo_langchain_agent()
