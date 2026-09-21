"""
AutoGPT示例
展示如何构建具有自主执行能力的Agent
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time

# ============ 数据结构定义 ============

class CommandType(Enum):
    """命令类型枚举
    
    定义AutoGPT可用的内置命令
    """
    SEARCH = "search"           # 搜索
    WRITE_FILE = "write_file"   # 写文件
    READ_FILE = "read_file"     # 读文件
    EXECUTE_CODE = "execute_code"  # 执行代码
    BROWSE = "browse"           # 浏览网页
    THINK = "think"             # 思考
    GOAL_COMPLETED = "goal_completed"  # 目标完成

@dataclass
class Memory:
    """记忆系统
    
    维护短期记忆和长期记忆
    模拟AutoGPT的记忆机制
    """
    short_term: List[str] = field(default_factory=list)  # 短期记忆：最近的操作
    long_term: List[Dict] = field(default_factory=list)  # 长期记忆：持久化的重要信息
    
    def add_short_term(self, item: str):
        """添加短期记忆
        
        参数:
            item: 记忆内容
        """
        self.short_term.append(item)
        # 保持短期记忆不超过10条，避免内存溢出
        if len(self.short_term) > 10:
            self.short_term.pop(0)
    
    def add_long_term(self, key: str, value: Any):
        """添加长期记忆
        
        参数:
            key: 记忆键
            value: 记忆值
        """
        self.long_term.append({
            "key": key,
            "value": value,
            "timestamp": time.time()
        })
    
    def recall(self, query: str) -> List[str]:
        """检索记忆
        
        参数:
            query: 查询关键词
        返回:
            相关记忆列表
        """
        results = []
        for item in self.long_term:
            # 简单的关键词匹配
            if query.lower() in str(item["value"]).lower():
                results.append(item["value"])
        return results

@dataclass
class Command:
    """命令定义
    
    表示Agent要执行的命令
    """
    type: CommandType           # 命令类型
    args: Dict[str, Any]        # 命令参数
    reasoning: str = ""         # 执行原因：解释为什么执行这个命令

@dataclass
class ExecutionResult:
    """执行结果
    
    封装命令执行后的输出
    """
    command: Command
    output: str
    success: bool = True
    should_continue: bool = True

# ============ AutoGPT核心实现 ============

class AutoGPTAgent:
    """AutoGPT风格的自主Agent
    
    核心能力：
    1. 自主分解目标
    2. 规划执行步骤
    3. 调用工具执行
    4. 评估结果并调整
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        goals: List[str],
        llm_client=None
    ):
        """初始化AutoGPT Agent
        
        参数:
            name: Agent名称
            role: Agent角色描述
            goals: 目标列表，Agent需要完成的目标
            llm_client: LLM客户端
        """
        self.name = name
        self.role = role
        self.goals = goals
        self.llm = llm_client
        
        # 核心组件初始化
        self.memory = Memory()              # 记忆系统
        self.commands_history: List[Command] = []  # 命令历史
        self.current_task: str = ""         # 当前任务
        
        # 配置参数
        self.max_iterations = 10            # 最大迭代次数
        self.iteration_count = 0            # 当前迭代计数
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词
        
        定义Agent的身份、目标和可用命令
        这是引导Agent自主行为的关键
        """
        goals_text = "\n".join([f"{i+1}. {goal}" for i, goal in enumerate(self.goals)])
        
        return f"""你是一个名为 {self.name} 的AI Agent。
角色：{role}

目标：
{goals_text}

你可以使用以下命令：
1. search <query> - 搜索信息
2. write_file <filename> <content> - 写入文件
3. read_file <filename> - 读取文件
4. think <thought> - 深入思考下一步
5. goal_completed - 标记目标完成

请以JSON格式输出你的决策：
{{
    "thoughts": {{
        "reasoning": "当前思考",
        "plan": "下一步计划",
        "criticism": "自我批评"
    }},
    "command": {{
        "name": "命令名称",
        "args": {{"参数名": "参数值"}}
    }}
}}
"""
    
    def start(self) -> Dict[str, Any]:
        """启动Agent执行主循环
        
        自主执行直到目标达成或达到最大迭代次数
        返回:
            执行结果汇总
        """
        print(f"\n🤖 {self.name} 启动！")
        print(f"📋 目标: {self.goals[0]}")
        print("-" * 50)
        
        # 主循环：持续执行直到条件满足
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            print(f"\n🔄 迭代 {self.iteration_count}/{self.max_iterations}")
            
            # 步骤1：思考下一步 - 自主决定行动
            command = self.think()
            
            # 步骤2：检查是否完成目标
            if command.type == CommandType.GOAL_COMPLETED:
                print("\n✅ 目标已完成！")
                break
            
            # 步骤3：执行命令
            result = self.execute(command)
            
            # 步骤4：记录到记忆
            self.memory.add_short_term(f"执行: {command.type.value} -> {result.output[:50]}")
            
            # 步骤5：评估结果
            if not result.should_continue:
                print("⚠️ 遇到问题，需要调整策略")
            
            print(f"   结果: {result.output[:100]}...")
        
        return self._generate_report()
    
    def think(self) -> Command:
        """思考下一步行动
        
        基于当前状态和历史，决定下一步命令
        这是AutoGPT的核心决策逻辑
        """
        # 构建上下文信息，供决策参考
        context = {
            "current_goal": self.goals[0],
            "memory": self.memory.short_term[-3:],  # 最近3条记忆
            "iteration": self.iteration_count
        }
        
        # 模拟LLM决策过程 - 实际应用中调用真实LLM
        # 根据迭代次数决定下一步行动
        if self.iteration_count == 1:
            return Command(
                type=CommandType.SEARCH,
                args={"query": self.goals[0]},
                reasoning="首先搜索相关信息，了解目标背景"
            )
        elif self.iteration_count == 2:
            return Command(
                type=CommandType.THINK,
                args={"thought": "分析搜索结果，规划下一步"},
                reasoning="整理思路，评估信息"
            )
        elif self.iteration_count == 3:
            return Command(
                type=CommandType.WRITE_FILE,
                args={
                    "filename": "result.txt",
                    "content": f"关于'{self.goals[0]}'的研究结果..."
                },
                reasoning="保存结果到文件，形成报告"
            )
        else:
            # 多次迭代后，认为目标已达成
            return Command(
                type=CommandType.GOAL_COMPLETED,
                args={},
                reasoning="目标已达成，结束执行"
            )
    
    def execute(self, command: Command) -> ExecutionResult:
        """执行命令
        
        根据命令类型执行相应的操作
        参数:
            command: 要执行的命令
        返回:
            执行结果
        """
        # 记录命令历史
        self.commands_history.append(command)
        
        print(f"   📌 执行: {command.type.value}")
        print(f"   📝 原因: {command.reasoning}")
        
        # 根据命令类型执行不同操作
        if command.type == CommandType.SEARCH:
            output = f"搜索'{command.args['query']}'的结果：找到5条相关信息"
            return ExecutionResult(command=command, output=output)
        
        elif command.type == CommandType.WRITE_FILE:
            filename = command.args["filename"]
            content = command.args["content"]
            output = f"成功写入文件 {filename}，共{len(content)}字符"
            # 保存到长期记忆，便于后续检索
            self.memory.add_long_term(filename, content)
            return ExecutionResult(command=command, output=output)
        
        elif command.type == CommandType.READ_FILE:
            filename = command.args["filename"]
            content = self.memory.recall(filename)
            output = content[0] if content else f"文件 {filename} 不存在"
            return ExecutionResult(command=command, output=output)
        
        elif command.type == CommandType.THINK:
            output = f"思考结论: {command.args['thought']}"
            return ExecutionResult(command=command, output=output)
        
        elif command.type == CommandType.GOAL_COMPLETED:
            return ExecutionResult(
                command=command,
                output="目标已完成",
                should_continue=False  # 标记不再继续
            )
        
        else:
            return ExecutionResult(
                command=command,
                output="未知命令",
                success=False
            )
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成执行报告
        
        汇总整个执行过程的统计信息
        """
        return {
            "agent_name": self.name,
            "goals": self.goals,
            "iterations": self.iteration_count,
            "commands_executed": len(self.commands_history),
            "memory_items": len(self.memory.long_term),
            "status": "completed" if self.iteration_count < self.max_iterations else "timeout"
        }

# ============ 使用示例 ============

def demo_autogpt():
    """演示AutoGPT的使用"""
    
    print("=" * 50)
    print("AutoGPT 自主Agent演示")
    print("=" * 50)
    
    # 创建Agent - 只需提供名称、角色和目标
    agent = AutoGPTAgent(
        name="ResearchBot",
        role="AI研究助手",
        goals=[
            "研究最新的AI Agent技术发展趋势",
            "整理关键发现并保存报告"
        ]
    )
    
    # 启动Agent - 完全自主执行
    result = agent.start()
    
    print("\n" + "=" * 50)
    print("📊 执行报告")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    demo_autogpt()
