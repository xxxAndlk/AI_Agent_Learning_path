"""
CrewAI示例
展示如何使用CrewAI构建多Agent协作系统
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import json

# ============ 核心数据结构 ============

class ProcessType(Enum):
    """任务执行流程类型
    
    定义CrewAI中任务执行的三种模式
    """
    SEQUENTIAL = "sequential"  # 顺序执行：任务按定义顺序依次执行
    PARALLEL = "parallel"      # 并行执行：所有任务同时开始执行
    HIERARCHICAL = "hierarchical"  # 层级执行：有管理者分配和审核任务

@dataclass
class AgentRole:
    """Agent角色定义
    
    精确定义每个Agent的角色、目标和背景
    这些信息会影响Agent的行为风格和输出
    """
    name: str              # 角色名称（如：研究员、作家、编辑）
    goal: str              # 角色目标：Agent需要达成的目标
    backstory: str         # 背景故事：影响Agent的行为风格和表达方式
    verbose: bool = False  # 是否输出详细日志

@dataclass
class Task:
    """任务定义
    
    描述需要完成的具体工作
    """
    description: str       # 任务描述：具体要做什么
    agent: 'CrewAgent' = None  # 负责该任务的Agent
    expected_output: str = ""  # 期望输出格式：指导Agent输出格式
    context: Dict = field(default_factory=dict)  # 任务上下文：传递给Agent的额外信息

@dataclass
class TaskResult:
    """任务执行结果
    
    封装任务执行后的输出和元数据
    """
    task: Task
    output: str
    success: bool = True
    execution_time: float = 0.0

# ============ CrewAI核心类实现 ============

class CrewAgent:
    """CrewAI风格的Agent
    
    每个Agent有特定的角色、目标和工具集
    通过角色定义影响Agent的行为和输出风格
    """
    
    def __init__(
        self,
        role: AgentRole,
        llm_client=None,
        tools: List[Callable] = None
    ):
        """初始化Agent
        
        参数:
            role: Agent角色定义，包含name、goal、backstory
            llm_client: LLM客户端（实际使用时传入真实LLM）
            tools: 可用工具列表
        """
        self.role = role
        self.llm = llm_client
        self.tools = tools or []
        self.memory: List[str] = []  # Agent的记忆：存储历史任务和输出
    
    def execute_task(self, task: Task, context: Dict = None) -> TaskResult:
        """执行任务
        
        参数:
            task: 要执行的任务
            context: 执行上下文（可能包含其他任务的输出）
        返回:
            任务执行结果
        """
        start_time = time.time()
        
        # 步骤1：构建提示词 - 融入角色信息
        prompt = self._build_prompt(task, context)
        
        # 步骤2：执行任务 - 模拟LLM生成输出
        output = self._generate_output(task, context)
        
        # 步骤3：记录到记忆 - 保持上下文连贯性
        self.memory.append(f"任务: {task.description}\n输出: {output}")
        
        execution_time = time.time() - start_time
        
        # 返回任务结果
        return TaskResult(
            task=task,
            output=output,
            success=True,
            execution_time=execution_time
        )
    
    def _build_prompt(self, task: Task, context: Dict = None) -> str:
        """构建提示词
        
        将角色信息和任务信息整合成完整的提示词
        参数:
            task: 任务对象
            context: 上下文信息
        返回:
            构建好的提示词
        """
        # 整合角色定义和任务要求
        prompt = f"""你是{self.role.name}。
目标：{self.role.goal}
背景：{self.role.backstory}

任务：{task.description}
期望输出：{task.expected_output}
"""
        # 如果有上下文，追加到提示词中
        if context:
            prompt += f"\n上下文信息：{context}\n"
        
        return prompt
    
    def _generate_output(self, task: Task, context: Dict = None) -> str:
        """生成输出（模拟LLM响应）
        
        根据角色类型生成不同风格的输出
        实际应用中应调用真实LLM
        """
        # 模拟不同角色的输出风格
        if "研究员" in self.role.name:
            return f"【研究报告】\n经过分析，关于'{task.description}'的研究结果如下：\n1. 关键发现A\n2. 关键发现B\n3. 建议采取的行动"
        elif "作家" in self.role.name:
            return f"【创作内容】\n基于研究材料，我撰写了以下内容：\n\n在当今时代，'{task.description}'是一个重要话题..."
        elif "编辑" in self.role.name:
            return f"【编辑审阅】\n内容已审阅，提出以下修改建议：\n- 优化标题\n- 调整段落结构\n- 补充数据支撑"
        elif "程序员" in self.role.name:
            return f"【代码实现】\n已完成功能开发：\n```python\ndef solution():\n    # 实现代码\n    pass\n```"
        else:
            return f"作为{self.role.name}，我已完成任务：{task.description}"

class Crew:
    """CrewAI风格的团队
    
    管理多个Agent协作完成任务
    支持多种执行流程
    """
    
    def __init__(
        self,
        agents: List[CrewAgent],
        tasks: List[Task],
        process: ProcessType = ProcessType.SEQUENTIAL
    ):
        """初始化团队
        
        参数:
            agents: Agent列表，团队成员
            tasks: 任务列表，需要完成的工作
            process: 执行流程类型
        """
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.results: List[TaskResult] = []  # 存储所有任务结果
    
    def kickoff(self) -> Dict[str, Any]:
        """启动团队协作
        
        按照指定的流程执行任务
        返回:
            执行结果汇总
        """
        print(f"\n🚀 Crew启动！执行模式: {self.process.value}")
        print(f"👥 团队成员: {', '.join([a.role.name for a in self.agents])}")
        print(f"📋 任务数量: {len(self.tasks)}")
        print("-" * 50)
        
        # 根据流程类型选择执行方式
        if self.process == ProcessType.SEQUENTIAL:
            return self._execute_sequential()
        elif self.process == ProcessType.PARALLEL:
            return self._execute_parallel()
        else:
            return self._execute_hierarchical()
    
    def _execute_sequential(self) -> Dict[str, Any]:
        """顺序执行任务
        
        每个任务依赖前一个任务的结果
        适用于任务之间有依赖关系的场景
        """
        context = {}
        
        for i, task in enumerate(self.tasks):
            print(f"\n📌 执行任务 {i+1}/{len(self.tasks)}: {task.description[:30]}...")
            
            if task.agent:
                # 执行任务并传入上下文（前面任务的结果）
                result = task.agent.execute_task(task, context)
                self.results.append(result)
                
                # 将结果加入上下文供后续任务使用
                context[f"task_{i}"] = result.output
                
                print(f"✅ 任务完成 (耗时: {result.execution_time:.2f}s)")
            else:
                print("⚠️ 任务未分配Agent，跳过")
        
        return self._summarize_results()
    
    def _execute_parallel(self) -> Dict[str, Any]:
        """并行执行任务
        
        所有任务同时开始执行
        适用于任务之间无依赖关系的场景
        """
        print("\n⚡ 并行执行所有任务...")
        
        # 模拟并行执行（实际可用多线程/多进程）
        for i, task in enumerate(self.tasks):
            if task.agent:
                result = task.agent.execute_task(task)
                self.results.append(result)
                print(f"✅ 任务{i+1}完成: {task.agent.role.name}")
        
        return self._summarize_results()
    
    def _execute_hierarchical(self) -> Dict[str, Any]:
        """层级执行任务
        
        有管理者分配和审核任务
        第一个Agent作为管理者，负责任务分配和结果审核
        """
        # 第一个Agent作为管理者
        manager = self.agents[0]
        workers = self.agents[1:]
        
        print(f"\n👔 管理者 {manager.role.name} 开始分配任务...")
        
        for i, task in enumerate(self.tasks):
            # 管理者分配任务给合适的工作者
            if i < len(workers):
                task.agent = workers[i]
                print(f"  → 分配给 {workers[i].role.name}")
            
            if task.agent:
                result = task.agent.execute_task(task)
                self.results.append(result)
        
        # 管理者审核所有结果
        print(f"\n👔 管理者 {manager.role.name} 审核结果...")
        for r in self.results:
            print(f"  ✓ 审核通过: {r.task.description[:20]}...")
        
        return self._summarize_results()
    
    def _summarize_results(self) -> Dict[str, Any]:
        """汇总结果
        
        将所有任务执行结果汇总成报告
        """
        return {
            "success": all(r.success for r in self.results),
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.results),
            "total_time": sum(r.execution_time for r in self.results),
            "results": [{"task": r.task.description, "output": r.output[:100]} for r in self.results]
        }

# ============ 使用示例 ============

def demo_crewai():
    """演示CrewAI的使用"""
    
    print("=" * 50)
    print("CrewAI 多Agent协作演示")
    print("=" * 50)
    
    # 定义角色 - 每个角色有明确的目标和背景
    researcher_role = AgentRole(
        name="高级研究员",
        goal="深入研究主题，收集全面信息",
        backstory="你是一位经验丰富的研究员，擅长数据分析和信息整合"
    )
    
    writer_role = AgentRole(
        name="内容作家",
        goal="将研究成果转化为引人入胜的内容",
        backstory="你是一位专业作家，擅长将复杂信息转化为易懂的文字"
    )
    
    editor_role = AgentRole(
        name="资深编辑",
        goal="确保内容质量，优化文章结构",
        backstory="你是一位严谨的编辑，追求完美和准确"
    )
    
    # 创建Agent实例
    researcher = CrewAgent(role=researcher_role)
    writer = CrewAgent(role=writer_role)
    editor = CrewAgent(role=editor_role)
    
    # 定义任务 - 每个任务分配给合适的Agent
    tasks = [
        Task(
            description="研究AI Agent技术的最新发展趋势",
            agent=researcher,
            expected_output="详细的研究报告，包含关键发现和建议"
        ),
        Task(
            description="基于研究结果撰写一篇技术博客文章",
            agent=writer,
            expected_output="结构清晰的博客文章初稿"
        ),
        Task(
            description="审核文章，提出修改建议",
            agent=editor,
            expected_output="审阅意见和修改后的最终版本"
        )
    ]
    
    # 创建团队 - 顺序执行模式
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=tasks,
        process=ProcessType.SEQUENTIAL
    )
    
    # 启动协作
    result = crew.kickoff()
    
    print("\n" + "=" * 50)
    print("📊 执行结果汇总")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    demo_crewai()
