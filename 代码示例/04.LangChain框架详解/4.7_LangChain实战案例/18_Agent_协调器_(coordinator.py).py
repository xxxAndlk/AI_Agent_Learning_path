"""
Agent 协调器
管理和协调多个 Agent 的协作
"""
import logging
from typing import Any, Dict, List, Optional, Callable
from langchain_openai import ChatOpenAI

from src.agents.base import BaseAgent, AgentConfig, Message
from src.agents.planner import PlannerAgent
from src.agents.research import ResearchAgent
from src.agents.coder import CoderAgent
from src.agents.reviewer import ReviewerAgent
from src.agents.executor import ExecutorAgent

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Agent 协调器"""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        model_name: str = "gpt-5.4-mini",
    ):
        """
        初始化协调器
        
        Args:
            llm: 语言模型
            model_name: 模型名称
        """
        self.llm = llm or ChatOpenAI(model=model_name)
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        
        # 初始化所有 Agent
        self._initialize_agents()
    
    def _initialize_agents(self):
        """初始化所有 Agent"""
        # 规划 Agent
        planner_config = AgentConfig(
            name="planner",
            description="任务规划 Agent",
            system_prompt="你是一个专业的任务规划专家。",
            model_name="gpt-5.4-mini",
        )
        self.agents["planner"] = PlannerAgent(planner_config, self.llm)
        
        # 研究 Agent
        research_config = AgentConfig(
            name="research",
            description="研究 Agent",
            system_prompt="你是一个专业的研究专家。",
            model_name="gpt-5.4-mini",
        )
        self.agents["research"] = ResearchAgent(research_config, self.llm)
        
        # 编码 Agent
        coder_config = AgentConfig(
            name="coder",
            description="编码 Agent",
            system_prompt="你是一个专业的程序员。",
            model_name="gpt-5.4-mini",
        )
        self.agents["coder"] = CoderAgent(coder_config, self.llm)
        
        # 审查 Agent
        reviewer_config = AgentConfig(
            name="reviewer",
            description="审查 Agent",
            system_prompt="你是一个资深的代码审查专家。",
            model_name="gpt-5.4-mini",
        )
        self.agents["reviewer"] = ReviewerAgent(reviewer_config, self.llm)
        
        # 执行 Agent
        executor_config = AgentConfig(
            name="executor",
            description="执行 Agent",
            system_prompt="你是一个任务执行专家。",
            model_name="gpt-5.4-mini",
        )
        self.agents["executor"] = ExecutorAgent(executor_config, self.llm)
        
        logger.info(f"初始化了 {len(self.agents)} 个 Agent")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """获取指定 Agent"""
        return self.agents.get(name)
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        执行复杂任务
        
        Args:
            task: 任务描述
            
        Returns:
            执行结果
        """
        logger.info(f"开始执行任务: {task}")
        
        # 第一步：规划
        planner = self.agents["planner"]
        plan = planner.process(task)
        
        logger.info(f"生成计划: {plan.get('goal')}")
        
        results = []
        
        # 第二步：按顺序执行子任务
        for subtask_id in plan.get("execution_order", []):
            if not planner.can_proceed(subtask_id):
                logger.warning(f"子任务 {subtask_id} 依赖未满足，跳过")
                continue
            
            subtask = next(
                (s for s in plan["subtasks"] if s["id"] == subtask_id),
                None
            )
            
            if not subtask:
                continue
            
            agent_type = subtask.get("agent", "research")
            agent = self.agents.get(agent_type)
            
            if not agent:
                logger.warning(f"未找到 Agent: {agent_type}")
                continue
            
            # 执行子任务
            logger.info(f"执行子任务 {subtask_id}: {subtask['description']}")
            
            try:
                result = agent.process({
                    "description": subtask["description"],
                    "task": task,
                })
                results.append({
                    "subtask_id": subtask_id,
                    "agent": agent_type,
                    "result": result,
                })
                
                # 更新任务状态
                planner.update_subtask_status(subtask_id, "completed")
                
            except Exception as e:
                logger.error(f"子任务 {subtask_id} 执行失败: {str(e)}")
                planner.update_subtask_status(subtask_id, "failed")
        
        # 第三步：综合结果
        final_result = self._synthesize_results(task, results)
        
        self.completed_tasks.append({
            "task": task,
            "plan": plan,
            "results": results,
            "final_result": final_result,
        })
        
        return final_result
    
    def _synthesize_results(
        self,
        original_task: str,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """综合所有子任务结果"""
        executor = self.agents["executor"]
        
        synthesis_task = {
            "type": "analysis",
            "data": f"""
原始任务: {original_task}

子任务执行结果:
{results}

请综合以上结果，提供最终答案。
            """,
        }
        
        return executor.process(synthesis_task)
    
    def send_message(
        self,
        sender: str,
        receiver: str,
        content: str,
    ):
        """Agent 之间发送消息"""
        message = Message(
            sender=sender,
            receiver=receiver,
            content=content,
        )
        
        sender_agent = self.agents.get(sender)
        if sender_agent:
            sender_agent.add_message(message)
        
        receiver_agent = self.agents.get(receiver)
        if receiver_agent:
            receiver_agent.add_message(message)
        
        logger.info(f"消息: {sender} -> {receiver}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有 Agent 的状态"""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "name": agent.config.name,
                "description": agent.config.description,
                "message_count": len(agent.message_history),
                "context_keys": list(agent.context.keys()),
            }
        return status
    
    def reset(self):
        """重置所有 Agent"""
        for agent in self.agents.values():
            agent.clear_history()
            agent.context.clear()
        
        self.task_queue.clear()
        logger.info("所有 Agent 已重置")
