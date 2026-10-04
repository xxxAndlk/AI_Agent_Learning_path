# 导入必要的类型提示和标准库模块
from typing import Dict, List, Any, Optional
import re
import os
from openai import OpenAI

# 从环境变量读取API密钥初始化客户端（安全做法，避免硬编码）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ReActAgent:
    """ReAct智能体实现
    
    通过交替推理和行动来解决问题
    这是一个完整的Agent框架，支持多轮对话和工具调用
    """
    
    def __init__(self, tools: Dict[str, Any], max_iterations: int = 10):
        """
        初始化ReActAgent智能体
        
        参数:
            tools: 可用工具的字典，key为工具名，value为工具函数
                   格式: {"工具名": 函数对象}
            max_iterations: 最大迭代次数，防止无限循环
                          超过此次数将强制终止并返回失败
        """
        # 将工具字典保存为实例变量，供后续方法使用
        self.tools = tools
        # 保存最大迭代次数配置
        self.max_iterations = max_iterations
        # 初始化空列表用于存储对话历史/记忆
        # 记忆用于保存之前的思考、行动和观察结果
        self.memory: List[Dict] = []
    
    def _think(self, query: str) -> str:
        """推理步骤：让模型思考下一步行动
        
        这是Agent的核心推理环节，会：
        1. 构建包含工具说明的提示词
        2. 将历史对话信息纳入上下文
        3. 调用LLM获取推理结果
        
        参数:
            query: 用户的问题或任务
            
        返回:
            模型返回的推理结果，包含思考和行动指令
        """
        # 构建工具描述文本，格式为 "- 工具名: 工具说明"
        # 遍历tools字典，为每个工具生成描述
        tool_descriptions = "\n".join([
            f"- {name}: {func.__doc__}" 
            for name, func in self.tools.items()
        ])
        
        # 从记忆构建历史记录，包含之前的思考、行动和观察
        # 格式: "思考: xxx\n行动: xxx\n观察: xxx"
        history = "\n".join([
            f"思考: {step.get('thought', '')}\n行动: {step.get('action', '')}\n观察: {step.get('observation', '')}"
            for step in self.memory
        ])
        
        # 构建完整的提示词，包含角色说明、可用工具、用户问题和历史
        prompt = f"""
        你是一个智能助手，可以使用以下工具：
        {tool_descriptions}
        
        用户问题: {query}
        
        {history}
        
        请按照以下格式回复：
        思考: [你的推理过程]
        行动: [工具名, 参数] 或 完成: [最终答案]
        """
        
        # 调用LLM API获取推理结果
        # 这里使用OpenAI GPT-5.4-mini模型作为示例
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        # 返回模型生成的内容
        return response.choices[0].message.content
    
    def _parse_action(self, text: str) -> Optional[tuple]:
        """解析模型回复中的行动指令
        
        使用正则表达式从模型输出中提取工具名和参数
        
        参数:
            text: 模型返回的完整文本
            
        返回:
            (工具名, 参数)的元组，或者None（如果解析失败）
        """
        # 匹配 "行动: 工具名, 参数" 格式
        # 正则解释: 行动: 空白字符 + 工具名 + 空白字符 + , + 空白字符 + 参数
        action_match = re.search(r'行动:\s*(\w+)\s*,\s*(.+)', text)
        if action_match:
            # 提取工具名并去除首尾空白
            tool_name = action_match.group(1).strip()
            # 提取参数并去除首尾空白
            params = action_match.group(2).strip()
            # 返回元组形式的解析结果
            return (tool_name, params)
        # 无法解析时返回None
        return None
    
    def _execute_action(self, action: tuple) -> str:
        """执行工具调用
        
        根据解析出的工具名和参数，调用对应的工具函数
        
        参数:
            action: (工具名, 参数)的元组
            
        返回:
            工具执行结果的字符串形式
        """
        # 解包元组获取工具名和参数
        tool_name, params = action
        # 检查工具是否在注册表中
        if tool_name in self.tools:
            try:
                # 调用工具函数并获取结果
                # 将参数转换为字符串传递
                result = self.tools[tool_name](params)
                return str(result)
            except Exception as e:
                # 捕获异常并返回错误信息
                return f"错误: {str(e)}"
        # 工具不存在时返回错误提示
        return f"未知工具: {tool_name}"
    
    def run(self, query: str) -> str:
        """运行ReAct循环
        
        这是Agent的主入口方法，执行完整的"推理-行动-观察"循环
        
        参数:
            query: 用户的问题或任务
            
        返回:
            任务完成的最终答案，或失败信息
        """
        # 打印任务标题，便于跟踪执行过程
        print(f"🎯 任务: {query}\n")
        
        # 迭代执行，直到任务完成或达到最大迭代次数
        for i in range(self.max_iterations):
            # ===== 第1步：推理 =====
            # 打印当前迭代轮次
            print(f"--- 迭代 {i+1} ---")
            # 调用_think方法获取模型推理结果
            response = self._think(query)
            # 打印模型回复内容
            print(f"🤔 模型回复:\n{response}\n")
            
            # ===== 第2步：提取思考 =====
            # 使用正则提取"思考:"后面的内容
            # (?=\n行动:|\n完成:|$) 表示匹配到行动:或完成:或字符串结尾为止
            thought_match = re.search(r'思考:\s*(.+?)(?=\n行动:|\n完成:|$)', response, re.DOTALL)
            # 如果找到则提取内容，否则为空字符串
            thought = thought_match.group(1).strip() if thought_match else ""
            
            # ===== 第3步：检查是否完成 =====
            # 判断模型是否返回了"完成:"标记
            if "完成:" in response:
                # 提取完成标记后的最终答案
                final_answer = re.search(r'完成:\s*(.+)', response)
                if final_answer:
                    # 提取答案内容
                    answer = final_answer.group(1).strip()
                    # 打印完成信息
                    print(f"✅ 任务完成: {answer}")
                    # 返回最终答案
                    return answer
            
            # ===== 第4步：解析并执行行动 =====
            # 尝试从模型回复中解析出行动指令
            action = self._parse_action(response)
            # 如果成功解析出行动
            if action:
                # 打印即将执行的行动
                print(f"🔧 执行行动: {action}")
                # 执行行动并获取观察结果
                observation = self._execute_action(action)
                # 打印观察结果
                print(f"👁️ 观察结果: {observation}\n")
                
                # ===== 第5步：保存到记忆 =====
                # 将本轮的思考、行动和观察结果保存到memory
                self.memory.append({
                    'thought': thought,  # 本轮推理内容
                    'action': f"{action[0]}({action[1]})",  # 格式化行动
                    'observation': observation  # 工具返回结果
                })
            else:
                # 无法解析行动时打印错误并退出循环
                print("❌ 无法解析行动")
                break
        
        # 达到最大迭代次数仍未完成任务时返回失败信息
        return "达到最大迭代次数，任务未完成"


# ==================== 示例工具定义 ====================

def search_tool(query: str) -> str:
    """搜索工具：模拟网络搜索
    
    这是一个示例工具，实际应用中应调用真实的搜索API（如Google、Bing等）
    
    参数:
        query: 搜索关键词
        
    返回:
        格式化的搜索结果字符串
    """
    # 实际应用中这里会调用真实搜索API
    # 例如: return google_search(query)
    return f"搜索结果: {query} 的相关信息..."

def calculator_tool(expression: str) -> str:
    """计算器工具：计算数学表达式
    
    支持基本数学运算：加、减、乘、除、括号
    
    参数:
        expression: 数学表达式字符串，如 "2+3*5"
        
    返回:
        计算结果或错误信息
    """
    try:
        # 安全计算：只允许基本数字和运算符字符
        # 定义允许的字符集合
        allowed_chars = set('0123456789+-*/.() ')
        # 检查表达式是否只包含允许的字符，防止注入攻击
        if all(c in allowed_chars for c in expression):
            # 使用eval计算表达式（实际生产环境建议使用安全解析器）
            result = eval(expression)
            return str(result)
        # 包含非法字符时返回错误
        return "无效的表达式"
    except Exception as e:
        # 捕获计算过程中的异常并返回错误信息
        return f"计算错误: {str(e)}"

def weather_tool(city: str) -> str:
    """天气工具：查询城市天气
    
    这是一个示例工具，实际应用中应调用真实天气API
    
    参数:
        city: 城市名称，如 "北京"、"上海"
        
    返回:
        天气信息字符串
    """
    # 模拟天气数据库，实际应用中应调用天气预报API
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，28°C",
        "深圳": "小雨，30°C"
    }
    # 查找城市天气，未找到时返回默认信息
    return weather_data.get(city, f"未找到{city}的天气信息")


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    # 创建工具注册表，将工具函数注册到字典中
    # 键为工具名（将在提示词中使用），值为函数对象
    tools = {
        "搜索": search_tool,      # 注册搜索工具
        "计算": calculator_tool,  # 注册计算器工具
        "天气": weather_tool      # 注册天气工具
    }
    
    # 创建ReActAgent实例，传入工具字典
    agent = ReActAgent(tools)
    
    # 运行Agent处理复杂任务
    # 这个任务包含两个子任务：查询天气 + 条件计算
    result = agent.run("北京今天的天气如何？如果气温超过26度，计算26度的80%是多少。")
    
    # 打印最终返回结果
    print(f"\n📝 最终结果: {result}")
