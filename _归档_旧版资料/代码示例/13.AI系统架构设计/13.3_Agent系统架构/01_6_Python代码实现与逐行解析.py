"""
Agent系统架构

Agent架构模式：
- ReAct: Thought-Action-Observation循环
- Plan & Execute: 先规划后执行
- Multi-Agent: 多Agent协作
"""

from typing import Dict, List, Any, Optional
from openai import OpenAI
import json
import os
import re


class TaskExecutionAgent:
    """任务执行Agent
    
    功能：
    - 理解用户任务需求
    - 自主规划执行步骤
    - 调用工具完成任务
    - 处理执行过程中的异常
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.memory: List[Dict] = []        # 记忆存储，保存历史推理和观察结果
        self.max_iterations = 10           # 最大迭代次数，防止无限循环
        
        # 注册工具字典，将工具名称映射到具体的工具函数
        self.tools = {
            "calculate": self._tool_calculate,      # 数学计算工具
            "search": self._tool_search,            # 搜索工具（模拟）
            "get_time": self._tool_get_time,        # 获取当前时间
            "file_read": self._tool_file_read,     # 文件读取工具
            "file_write": self._tool_file_write     # 文件写入工具
        }
    
    def _tool_calculate(self, expression: str) -> str:
        """计算器工具：安全地执行数学表达式计算"""
        try:
            # 安全检查：只允许数字和基本运算符
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)  # 计算表达式结果
                return str(result)
            return "错误：表达式包含非法字符"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    def _tool_search(self, query: str) -> str:
        """搜索工具（模拟）：返回模拟的搜索结果"""
        return f"搜索结果：找到关于'{query}'的相关信息..."
    
    def _tool_get_time(self, _=None) -> str:
        """获取当前时间：返回当前日期时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _tool_file_read(self, filepath: str) -> str:
        """读取文件工具：从指定路径读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()[:1000]  # 限制返回长度
        except Exception as e:
            return f"读取失败: {str(e)}"
    
    def _tool_file_write(self, params: str) -> str:
        """写入文件工具：格式为"文件路径|内容" """
        try:
            parts = params.split('|', 1)  # 使用|分割路径和内容
            if len(parts) != 2:
                return "格式错误，使用: 文件路径|内容"
            filepath, content = parts
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"成功写入文件: {filepath}"
        except Exception as e:
            return f"写入失败: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """获取系统提示：定义Agent的行为规范和工具说明"""
        # 生成所有工具的描述列表
        tool_descriptions = "\n".join([
            f"- {name}: {func.__doc__}" 
            for name, func in self.tools.items()
        ])
        
        return f"""你是一个智能任务执行助手。你可以使用以下工具来完成任务：

{tool_descriptions}

请按以下格式回复：
思考: [你的分析和计划]
行动: [工具名] [参数]
或
完成: [任务结果]

注意：
1. 每次只执行一个工具
2. 观察工具返回后继续下一步
3. 如果任务完成，使用"完成:"格式回复
"""
    
    def execute_task(self, task: str) -> str:
        """执行任务：主入口，启动Agent的任务执行循环"""
        print(f"🎯 任务: {task}\n")
        
        # 清空历史记忆，准备新一轮任务执行
        self.memory = []
        
        # 迭代执行：思考->行动->观察循环
        for iteration in range(self.max_iterations):
            print(f"--- 迭代 {iteration + 1} ---")
            
            # 构建消息：包含系统提示、用户任务和历史记忆
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"任务: {task}"}
            ]
            
            # 添加历史记忆，帮助Agent了解任务进度
            for mem in self.memory:
                messages.append({"role": "assistant", "content": mem["response"]})
                messages.append({"role": "user", "content": f"观察: {mem['observation']}"})
            
            # 调用LLM获取Agent的决策
            response = self.client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=messages,
                temperature=0
            )
            
            content = response.choices[0].message.content
            print(f"🤔 助手:\n{content}\n")
            
            # 检查任务是否完成
            if "完成:" in content:
                result = content.split("完成:", 1)[1].strip()
                print(f"✅ 任务完成: {result}")
                return result
            
            # 解析行动指令，提取工具名和参数
            action_match = re.search(r'行动:\s*(\w+)\s*(.+)?', content, re.DOTALL)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_params = action_match.group(2).strip() if action_match.group(2) else ""
                
                print(f"🔧 执行: {tool_name}({tool_params})")
                
                # 执行工具调用
                if tool_name in self.tools:
                    try:
                        observation = self.tools[tool_name](tool_params)
                    except Exception as e:
                        observation = f"工具执行错误: {str(e)}"
                else:
                    observation = f"未知工具: {tool_name}"
                
                print(f"👁️ 观察: {observation}\n")
                
                # 保存到记忆，供下一轮迭代使用
                self.memory.append({
                    "response": content,
                    "observation": observation
                })
            else:
                print("❌ 无法解析行动，任务中断")
                break
        
        return "任务未完成，达到最大迭代次数"


if __name__ == "__main__":
    agent = TaskExecutionAgent()
    
    # 测试任务
    tasks = [
        "计算 (15 + 25) * 3 / 5 的结果",
    ]
    
    for task in tasks:
        result = agent.execute_task(task)
        print(f"最终结果: {result}\n")
